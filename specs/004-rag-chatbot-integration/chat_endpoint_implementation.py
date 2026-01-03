"""
Chat API endpoint for the RAG Agent system.

This module defines the FastAPI endpoint for chat interactions with the RAG agent,
allowing users to ask questions about book content and receive grounded responses
with source citations.
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any, List, Optional
import time
import logging
from pydantic import BaseModel

from src.models.request import QueryRequest, QueryResponse, SourceReference
from src.services.embedding import EmbeddingService
from src.services.retrieval import RetrievalService
from src.config.settings import settings
from src.middleware import get_api_key, verify_api_key


# Create API router
router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_embedding_service():
    """Dependency for embedding service."""
    return EmbeddingService()


def get_retrieval_service():
    """Dependency for retrieval service."""
    return RetrievalService(get_embedding_service())


class MockAgentService:
    """Mock agent service for testing when API keys are not available."""

    def generate_response(self, question: str, retrieved_docs):
        """Generate a mock response based on the question and retrieved docs."""
        from src.models.agent import AgentResponse, RetrievedDocument

        # Create a mock response
        if retrieved_docs:
            # Create a response based on the first document
            first_doc_content = retrieved_docs[0].content[:200] if retrieved_docs else "No content available"
            answer = f"Based on the retrieved information: '{first_doc_content[:100]}...', here is the answer to your question: {question}"
        else:
            answer = f"I found your question '{question}' interesting, but I couldn't find specific content in the book to answer it. Please check if the book contains relevant information."

        return AgentResponse(
            answer=answer,
            sources=retrieved_docs,
            retrieval_metadata={
                "retrieved_count": len(retrieved_docs),
                "model_used": "mock_model",
                "reasoning_completed": True
            }
        )


def get_agent_service():
    """Dependency for agent service."""
    try:
        from src.services.agent_service import AgentService
        return AgentService()
    except RuntimeError as e:
        if "OPENAI_API_KEY" in str(e):
            logger.warning(f"Agent service not available due to missing API key: {e}")
            logger.info("Using mock agent service for testing purposes")
            return MockAgentService()
        else:
            raise


async def authenticate_api_key(request: Request):
    """Dependency to authenticate API key."""
    api_key = get_api_key(request)
    if not verify_api_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )


class ChatRequest(BaseModel):
    """
    Request model for chat interactions.
    """
    query: str
    selected_text: Optional[str] = None
    top_k: Optional[int] = settings.top_k_default
    include_sources: bool = True


class ChatSource(BaseModel):
    """
    Source reference for chat responses.
    """
    content: str
    metadata: Dict[str, Any]
    url: Optional[str] = None
    title: Optional[str] = None


class ChatResponse(BaseModel):
    """
    Response model for chat interactions.
    """
    response: str
    sources: List[ChatSource]
    query_id: str
    timing: Dict[str, float]


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    _: str = Depends(authenticate_api_key),  # Authentication dependency
    embed_service: EmbeddingService = Depends(get_embedding_service),
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    agent_service = Depends(get_agent_service)
):
    """
    Chat endpoint for the RAG agent.

    Accepts a user query, retrieves relevant book content, and returns an answer
    with source references.
    """
    try:
        # Validate query
        if not request.query or not request.query.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "INVALID_QUERY",
                    "message": "Query cannot be empty"
                }
            )

        # Validate query length
        if len(request.query) > 1000:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "INVALID_QUERY",
                    "message": "Query must be less than 1000 characters"
                }
            )

        # Validate top_k if provided
        if request.top_k is not None:
            if not (settings.top_k_min <= request.top_k <= settings.top_k_max):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "INVALID_TOP_K",
                        "message": f"top_k must be between {settings.top_k_min} and {settings.top_k_max}"
                    }
                )

        # Use default top_k if not provided
        top_k = request.top_k or settings.top_k_default

        # Measure the time for the entire operation
        start_time = time.time()

        # Log the incoming query for monitoring
        logger.info(f"Processing chat query: {request.query[:50]}...")

        # Prepare the query - if selected_text is provided, focus on it
        effective_query = request.query
        if request.selected_text:
            effective_query = f"Based on this text: '{request.selected_text}', answer this question: {request.query}"

        # Retrieve relevant documents
        retrieval_start = time.time()
        retrieved_docs = retrieval_service.retrieve_documents(
            query=effective_query,
            top_k=top_k
        )
        retrieval_time = time.time() - retrieval_start

        # Log retrieval information
        logger.info(f"Retrieved {len(retrieved_docs)} documents in {retrieval_time:.2f}s")

        # Generate response using the agent
        agent_start = time.time()
        agent_response = agent_service.generate_response(
            question=effective_query,
            retrieved_docs=retrieved_docs
        )
        agent_time = time.time() - agent_start

        # Log agent processing time
        logger.info(f"Agent processed query in {agent_time:.2f}s")

        # Calculate total time
        total_time = time.time() - start_time

        # Create source references for the response
        chat_sources = []
        if request.include_sources:
            for doc in retrieved_docs:  # Use retrieved_docs which is the full RetrievedDocument
                source = ChatSource(
                    content=doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                    metadata=doc.metadata,
                    url=doc.metadata.get('url'),
                    title=doc.metadata.get('title', doc.metadata.get('heading_path', 'Unknown'))
                )
                chat_sources.append(source)

        # Create and return the response
        response = ChatResponse(
            response=agent_response.answer,
            sources=chat_sources,
            query_id=f"chat-{int(time.time())}-{abs(hash(request.query)) % 10000:04d}",
            timing={
                "retrieval_time": retrieval_time,
                "agent_time": agent_time,
                "total_time": total_time
            }
        )

        logger.info(f"Chat query completed in {total_time:.2f}s")
        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error with traceback
        logger.error(f"Error processing chat query: {str(e)}", exc_info=True)
        # Raise a 500 error for any other exceptions
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": f"Internal server error: {str(e)}"
            }
        )


@router.get("/chat/health")
async def chat_health_check():
    """
    Health check endpoint for the chat service.
    """
    return {"status": "healthy", "service": "Chat API"}