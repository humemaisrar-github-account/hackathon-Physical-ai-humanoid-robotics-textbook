#!/usr/bin/env python3
"""
Minimal RAG Chatbot Backend using OpenRouter API and Qdrant Cloud
"""
import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import httpx
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="RAG Chatbot Backend", version="1.0.0")

# Models
class ChatRequest(BaseModel):
    query: str
    selected_text: Optional[str] = None
    top_k: int = 3
    include_sources: bool = True

class Source(BaseModel):
    content: str
    metadata: Dict[str, Any]
    url: str = None
    title: str = "Unknown"

class ChatResponse(BaseModel):
    response: str
    sources: List[Source]
    query_id: str
    timing: Dict[str, float]

# Global variables
client = None
qdrant_client = None

def init_clients():
    """Initialize OpenRouter client and Qdrant client"""
    global client, qdrant_client

    # Initialize OpenRouter client
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")

    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

    # Initialize Qdrant client
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    if not qdrant_url or not qdrant_api_key:
        raise ValueError("QDRANT_URL and QDRANT_API_KEY environment variables are required")

    # For simplicity, we'll use httpx to make direct requests to Qdrant
    qdrant_client = httpx.Client(base_url=qdrant_url, headers={
        "Content-Type": "application/json",
        "api-key": qdrant_api_key
    })

@app.on_event("startup")
async def startup_event():
    """Initialize clients on startup"""
    try:
        init_clients()
        logger.info("RAG Chatbot backend initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize clients: {e}")
        raise

def search_qdrant(query: str, top_k: int = 3) -> List[Dict]:
    """Search Qdrant Cloud for relevant documents"""
    global qdrant_client

    try:
        search_payload = {
            "vector": query,  # This would normally be an embedding, but we'll use the query text
            "limit": top_k,
            "with_payload": True,
            "with_vectors": False
        }

        # Note: This is a simplified example. In a real implementation,
        # you would need to generate embeddings for the query
        response = qdrant_client.post(
            "/collections/text_embeddings/points/search",
            content=json.dumps(search_payload)
        )

        if response.status_code == 200:
            results = response.json()
            return results.get("result", [])
        else:
            logger.warning(f"Qdrant search failed: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        logger.error(f"Error searching Qdrant: {e}")
        return []

def query_openrouter(context: str, query: str, selected_text: str = None) -> str:
    """Query OpenRouter API with context and query"""
    global client

    try:
        # Build the system message with strict instructions
        system_message = {
            "role": "system",
            "content": "You are a helpful study assistant for a book. Answer questions STRICTLY based on the provided book content only. Do not generate answers from general knowledge. If the answer is not found in the book content, reply clearly: 'This information is not available in the book.' Keep responses short, clear, and professional. Use simple English. Do not use emojis in responses."
        }

        # Build the user message with context
        if selected_text:
            user_message = {
                "role": "user",
                "content": f"""
Book content:
{context}

Selected text:
{selected_text}

Question: {query}

Answer the question based on the selected text and book content above. If the answer is not in the provided content, reply: 'This information is not available in the book.'
"""
            }
        else:
            user_message = {
                "role": "user",
                "content": f"""
Book content:
{context}

Question: {query}

Answer the question based on the book content above. If the answer is not in the provided content, reply: 'This information is not available in the book.'
"""
            }

        # Make the API call to OpenRouter
        response = client.chat.completions.create(
            model="mistralai/devstral-2512:free",
            messages=[system_message, user_message],
            temperature=0.1,
            max_tokens=500
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Error querying OpenRouter: {e}")
        if "429" in str(e) or "rate limit" in str(e).lower():
            return "Rate limit exceeded. Please wait a moment before asking another question."
        return "Error generating response from the agent."

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat endpoint for the RAG agent"""
    try:
        # Search Qdrant for relevant documents
        retrieved_docs = search_qdrant(request.query, request.top_k)

        # Build context from retrieved documents
        if retrieved_docs:
            context = "\n\n".join([
                doc.get("payload", {}).get("content", "") or doc.get("content", "")
                for doc in retrieved_docs
            ])
        else:
            context = ""

        # Query OpenRouter with context
        response_text = query_openrouter(context, request.query, request.selected_text)

        # Format sources
        sources = []
        if request.include_sources and retrieved_docs:
            for doc in retrieved_docs:
                payload = doc.get("payload", {})
                sources.append(Source(
                    content=payload.get("content", "")[:200] + "..." if len(payload.get("content", "")) > 200 else payload.get("content", ""),
                    metadata=payload.get("metadata", {}),
                    url=payload.get("url"),
                    title=payload.get("title", payload.get("heading_path", "Unknown"))
                ))

        # Create response
        response = ChatResponse(
            response=response_text,
            sources=sources,
            query_id=f"chat-{hash(request.query) % 10000:04d}",
            timing={"total_time": 0.0}  # Timing would be calculated in a real implementation
        )

        return response

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "RAG Chatbot API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)