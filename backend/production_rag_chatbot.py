#!/usr/bin/env python3
"""
Production-Ready Book-Based RAG Chatbot using OpenRouter
"""
import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http import models
import numpy as np
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Book-Based RAG Chatbot", version="1.0.0")

# Models
class ChatRequest(BaseModel):
    query: str
    top_k: int = 3
    include_sources: bool = True

class Source(BaseModel):
    content: str
    metadata: Dict[str, Any]
    score: float

class ChatResponse(BaseModel):
    response: str
    sources: List[Source]
    query_id: str

# Global variables
openai_client = None
qdrant_client = None

def init_services():
    """Initialize OpenAI client, Qdrant client"""
    global openai_client, qdrant_client

    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    base_url = os.getenv("OPENAI_BASE_URL", "https://api.chatanywhere.org/v1")

    openai_client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    # Initialize Qdrant client
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    if not qdrant_url or not qdrant_api_key:
        raise ValueError("QDRANT_URL and QDRANT_API_KEY environment variables are required")

    qdrant_client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key,
        timeout=10
    )

    logger.info("Services initialized successfully")

def embed_text(text: str) -> List[float]:
    """Embed text using Cohere embeddings (to match existing database)"""
    # Use Cohere API for embedding to match the existing 1024-dim vectors in the database
    import cohere
    cohere_api_key = os.getenv("COHERE_API_KEY")
    if not cohere_api_key:
        raise ValueError("COHERE_API_KEY environment variable is required for embeddings")

    cohere_client = cohere.Client(cohere_api_key)

    response = cohere_client.embed(
        texts=[text],
        model="embed-english-v3.0",  # Same model used for indexing
        input_type="search_query"
    )
    embedding = response.embeddings[0]
    return embedding

def retrieve_context(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Retrieve relevant context from Qdrant based on the query"""
    global qdrant_client

    try:
        # Embed the query
        query_vector = embed_text(query)

        # Search in Qdrant - using the correct method signature
        from qdrant_client.http import models

        search_result = qdrant_client.query_points(
            collection_name="text_embeddings",  # Using same method as end-to-end pipeline
            query=query_vector,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )

        # Extract relevant documents
        retrieved_docs = []
        for hit in search_result:
            # Use 'text' field which matches the payload structure from the embedding pipeline
            content = hit.payload.get("text", "") if hasattr(hit, 'payload') and hit.payload else ""
            if not content:  # Fallback to 'content' if 'text' doesn't exist
                content = hit.payload.get("content", "") if hasattr(hit, 'payload') and hit.payload else ""
            retrieved_docs.append({
                "content": content,
                "metadata": hit.payload if hasattr(hit, 'payload') and hit.payload else {},
                "score": hit.score if hasattr(hit, 'score') else 0.0
            })

        return retrieved_docs

    except AttributeError as e:
        logger.error(f"AttributeError retrieving context from Qdrant: {e}")
        # Fallback: return empty list if search method is not available
        return []
    except Exception as e:
        logger.error(f"Error retrieving context from Qdrant: {e}")
        # Check if it's a rate limiting error
        error_msg = str(e).lower()
        if "429" in error_msg or "rate limit" in error_msg or "too many requests" in error_msg:
            logger.warning(f"Rate limit hit when embedding query: {query}")
        return []

def generate_response(context: str, query: str) -> str:
    """Generate response using OpenRouter API with context"""
    global openai_client

    try:
        # Prepare system message with strict instructions
        system_message = {
            "role": "system",
            "content": "You are a book-based assistant. You must answer strictly using the provided book context. If the answer is not present in the context, say: 'this information is not available in the book.' Do not use any external knowledge."
        }

        # Prepare user message with context and query
        user_message = {
            "role": "user",
            "content": f"""
Book Context:
{context}

Question: {query}

Please answer the question based on the provided book context. If the answer is not explicitly available in the context, respond with: 'this information is not available in the book.'
"""
        }

        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Using OpenAI's model as required
            messages=[system_message, user_message],
            temperature=0.1,  # Low temperature for consistent responses
            max_tokens=500
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Error generating response: {e}")
        if "429" in str(e) or "rate limit" in str(e).lower():
            return "Rate limit exceeded. Please wait a moment before asking another question."
        return "Error generating response from the agent."

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        init_services()
        logger.info("RAG Chatbot initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for the RAG agent"""
    try:
        # Retrieve relevant context from Qdrant
        retrieved_docs = retrieve_context(request.query, request.top_k)

        # Build context string from retrieved documents
        if retrieved_docs:
            context = "\n\n".join([doc["content"] for doc in retrieved_docs])
        else:
            context = ""

        # Generate response using OpenRouter with the context
        response_text = generate_response(context, request.query)

        # Format sources
        sources = []
        if request.include_sources and retrieved_docs:
            for doc in retrieved_docs:
                sources.append(Source(
                    content=doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
                    metadata=doc["metadata"],
                    score=doc["score"]
                ))

        # Create and return response
        response = ChatResponse(
            response=response_text,
            sources=sources,
            query_id=f"chat-{hash(request.query) % 10000:04d}"
        )

        return response

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Book-Based RAG Chatbot API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)