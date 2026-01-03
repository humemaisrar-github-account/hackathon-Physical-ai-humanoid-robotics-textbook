"""
Query API endpoint for the RAG Agent system.

This module defines the FastAPI endpoint for submitting questions and receiving
answers with source references.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any
import time
import logging
from src.models.request import QueryRequest, QueryResponse, SourceReference
from src.services.embedding import EmbeddingService
from src.services.retrieval import RetrievalService
from src.services.agent_service import AgentService
from src.config.settings import settings
from src.middleware import get_api_key, verify_api_key


# Create API router
router = APIRouter()

# Initialize services (in a real application, you'd want to use dependency injection)
embedding_service = EmbeddingService()
retrieval_service = RetrievalService(embedding_service)
agent_service = AgentService()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_embedding_service():
    """Dependency for embedding service."""
    return embedding_service


def get_retrieval_service():
    """Dependency for retrieval service."""
    return retrieval_service


def get_agent_service():
    """Dependency for agent service."""
    return agent_service


async def authenticate_api_key(request: Request):
    """Dependency to authenticate API key."""
    api_key = get_api_key(request)
    if not verify_api_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )


@router.post("/query", response_model=QueryResponse)
async def query_endpoint(
    request: QueryRequest,
    _: str = Depends(authenticate_api_key),  # Authentication dependency
    embed_service: EmbeddingService = Depends(get_embedding_service),
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Submit a question to the RAG agent.

    Accepts a user question, retrieves relevant book content, and returns an answer
    with source references.
    """
    try:
        # Pydantic model validation already handles most validation
        # but we'll add explicit checks as required

        # Additional validation for question length (though Pydantic handles this too)
        if not (1 <= len(request.question) <= 1000):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "INVALID_QUESTION",
                    "message": "Question must be between 1 and 1000 characters"
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
        logger.info(f"Processing query: {request.question[:50]}...")

        # Retrieve relevant documents
        retrieval_start = time.time()
        retrieved_docs = retrieval_service.retrieve_documents(
            query=request.question,
            top_k=top_k
        )
        retrieval_time = time.time() - retrieval_start

        # Log retrieval information
        logger.info(f"Retrieved {len(retrieved_docs)} documents in {retrieval_time:.2f}s")

        # Generate response using the agent
        agent_start = time.time()
        agent_response = agent_service.generate_response(
            question=request.question,
            retrieved_docs=retrieved_docs
        )
        agent_time = time.time() - agent_start

        # Log agent processing time
        logger.info(f"Agent processed query in {agent_time:.2f}s")

        # Calculate total time
        total_time = time.time() - start_time

        # Update the agent response with timing information
        if agent_response.retrieval_metadata is None:
            agent_response.retrieval_metadata = {}
        agent_response.retrieval_metadata.update({
            "query_time": retrieval_time,
            "agent_time": agent_time,
            "total_time": total_time
        })

        # Log the completion
        logger.info(f"Query completed in {total_time:.2f}s")

        # Create source references for the response
        source_references = []
        if request.include_sources:
            for doc in agent_response.sources:  # Use agent_response.sources which is the full RetrievedDocument
                source_references.append(
                    SourceReference(
                        content=doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                        metadata=doc.metadata,
                        relevance_score=doc.score
                    )
                )

        # Create and return the response
        response = QueryResponse(
            answer=agent_response.answer,
            sources=source_references,
            query_id=f"query-{int(time.time())}-{abs(hash(request.question)) % 10000:04d}"
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error with traceback
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        # Raise a 500 error for any other exceptions
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": f"Internal server error: {str(e)}"
            }
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return {"status": "healthy", "service": "RAG Agent API"}