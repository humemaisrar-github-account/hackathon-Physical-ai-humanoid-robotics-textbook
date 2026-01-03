"""
API endpoints for the Text Embedding Service.

This module defines FastAPI endpoints for:
1. Converting text to embeddings
2. Saving embeddings to Qdrant
3. Retrieving similar embeddings from Qdrant
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Dict, Any, Optional
import time
import logging

from src.models.request import QueryRequest, QueryResponse, SourceReference
from src.services.text_embedding_service import TextEmbeddingService, create_text_embedding_service
from src.config.settings import settings
from src.middleware import get_api_key, verify_api_key


# Create API router
router = APIRouter()

# Initialize services
text_embedding_service = create_text_embedding_service()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_text_embedding_service():
    """Dependency for text embedding service."""
    return text_embedding_service


# Request/Response models for the new endpoints
from pydantic import BaseModel


class TextEmbeddingRequest(BaseModel):
    """Request model for text embedding operations."""
    texts: List[str]
    metadata_list: Optional[List[Dict[str, Any]]] = None


class TextEmbeddingResponse(BaseModel):
    """Response model for text embedding operations."""
    success: bool
    message: str
    embeddings: Optional[List[List[float]]] = None
    ids: Optional[List[str]] = None
    count: Optional[int] = None


class SimilaritySearchRequest(BaseModel):
    """Request model for similarity search operations."""
    query_text: str
    top_k: Optional[int] = 5
    filters: Optional[Dict[str, Any]] = None


class SimilarityResult(BaseModel):
    """Model for individual similarity search result."""
    id: str
    score: float
    text: str
    payload: Dict[str, Any]


class SimilaritySearchResponse(BaseModel):
    """Response model for similarity search operations."""
    success: bool
    message: str
    results: List[SimilarityResult]
    query_text: str


class CountResponse(BaseModel):
    """Response model for count operations."""
    success: bool
    count: int
    message: str


class DeleteRequest(BaseModel):
    """Request model for delete operations."""
    ids: List[str]


class DeleteResponse(BaseModel):
    """Response model for delete operations."""
    success: bool
    deleted_count: int
    message: str


async def authenticate_api_key(request: Request):
    """Dependency to authenticate API key."""
    api_key = get_api_key(request)
    if not verify_api_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )


@router.post("/embed", response_model=TextEmbeddingResponse)
async def embed_texts(
    request: TextEmbeddingRequest,
    service: TextEmbeddingService = Depends(get_text_embedding_service)
):
    """
    Convert a list of texts to embeddings using Cohere.
    """
    try:
        logger.info(f"Processing embedding request for {len(request.texts)} texts")

        if not request.texts:
            raise HTTPException(
                status_code=400,
                detail={"error": "INVALID_INPUT", "message": "Texts list cannot be empty"}
            )

        # Validate text count
        if len(request.texts) > 100:  # Reasonable limit
            raise HTTPException(
                status_code=400,
                detail={"error": "INVALID_INPUT", "message": "Too many texts provided (max 100)"}
            )

        # Generate embeddings
        start_time = time.time()
        embeddings = service.convert_text_to_embeddings(request.texts)
        processing_time = time.time() - start_time

        logger.info(f"Successfully generated embeddings in {processing_time:.2f}s")

        return TextEmbeddingResponse(
            success=True,
            message=f"Successfully generated {len(embeddings)} embeddings",
            embeddings=embeddings,
            count=len(embeddings)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing embedding request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": "INTERNAL_ERROR", "message": f"Internal server error: {str(e)}"}
        )


@router.post("/save", response_model=TextEmbeddingResponse)
async def save_embeddings(
    request: TextEmbeddingRequest,
    service: TextEmbeddingService = Depends(get_text_embedding_service)
):
    """
    Save text embeddings to Qdrant with appropriate IDs and metadata.
    """
    try:
        logger.info(f"Processing save request for {len(request.texts)} texts")

        if not request.texts:
            raise HTTPException(
                status_code=400,
                detail={"error": "INVALID_INPUT", "message": "Texts list cannot be empty"}
            )

        # Validate text count
        if len(request.texts) > 100:  # Reasonable limit
            raise HTTPException(
                status_code=400,
                detail={"error": "INVALID_INPUT", "message": "Too many texts provided (max 100)"}
            )

        # Save embeddings to Qdrant
        start_time = time.time()
        saved_ids = service.save_embeddings_to_qdrant(
            texts=request.texts,
            metadata_list=request.metadata_list
        )
        processing_time = time.time() - start_time

        logger.info(f"Successfully saved {len(saved_ids)} embeddings in {processing_time:.2f}s")

        return TextEmbeddingResponse(
            success=True,
            message=f"Successfully saved {len(saved_ids)} embeddings to Qdrant",
            ids=saved_ids,
            count=len(saved_ids)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing save request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": "INTERNAL_ERROR", "message": f"Internal server error: {str(e)}"}
        )


@router.post("/search", response_model=SimilaritySearchResponse)
async def search_similar(
    request: SimilaritySearchRequest,
    service: TextEmbeddingService = Depends(get_text_embedding_service)
):
    """
    Retrieve the most similar embeddings from Qdrant based on a query text.
    """
    try:
        logger.info(f"Processing similarity search for query: {request.query_text[:50]}...")

        if not request.query_text or not request.query_text.strip():
            raise HTTPException(
                status_code=400,
                detail={"error": "INVALID_INPUT", "message": "Query text cannot be empty"}
            )

        # Validate top_k
        if request.top_k is not None and (request.top_k < 1 or request.top_k > 100):
            raise HTTPException(
                status_code=400,
                detail={"error": "INVALID_TOP_K", "message": "top_k must be between 1 and 100"}
            )

        # Perform similarity search
        start_time = time.time()
        results = service.retrieve_similar_embeddings(
            query_text=request.query_text,
            top_k=request.top_k or 5
        )
        processing_time = time.time() - start_time

        logger.info(f"Found {len(results)} similar embeddings in {processing_time:.2f}s")

        # Convert results to response format
        similarity_results = [
            SimilarityResult(
                id=result["id"],
                score=result["score"],
                text=result["text"],
                payload=result["payload"]
            )
            for result in results
        ]

        return SimilaritySearchResponse(
            success=True,
            message=f"Successfully found {len(similarity_results)} similar embeddings",
            results=similarity_results,
            query_text=request.query_text
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing search request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": "INTERNAL_ERROR", "message": f"Internal server error: {str(e)}"}
        )


@router.get("/count", response_model=CountResponse)
async def get_embedding_count(
    service: TextEmbeddingService = Depends(get_text_embedding_service)
):
    """
    Get the total count of embeddings in the Qdrant collection.
    """
    try:
        logger.info("Processing count request")

        start_time = time.time()
        count = service.get_embedding_count()
        processing_time = time.time() - start_time

        logger.info(f"Retrieved count ({count}) in {processing_time:.2f}s")

        return CountResponse(
            success=True,
            count=count,
            message=f"Total embeddings in collection: {count}"
        )
    except Exception as e:
        logger.error(f"Error processing count request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": "INTERNAL_ERROR", "message": f"Internal server error: {str(e)}"}
        )


@router.post("/delete", response_model=DeleteResponse)
async def delete_embeddings(
    request: DeleteRequest,
    service: TextEmbeddingService = Depends(get_text_embedding_service)
):
    """
    Delete embeddings from Qdrant by their IDs.
    """
    try:
        logger.info(f"Processing delete request for {len(request.ids)} IDs")

        if not request.ids:
            raise HTTPException(
                status_code=400,
                detail={"error": "INVALID_INPUT", "message": "IDs list cannot be empty"}
            )

        # Delete embeddings
        start_time = time.time()
        success = service.delete_embeddings_by_ids(request.ids)
        processing_time = time.time() - start_time

        if success:
            logger.info(f"Successfully deleted {len(request.ids)} embeddings in {processing_time:.2f}s")
            return DeleteResponse(
                success=True,
                deleted_count=len(request.ids),
                message=f"Successfully deleted {len(request.ids)} embeddings"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail={"error": "DELETE_FAILED", "message": "Failed to delete embeddings"}
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing delete request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": "INTERNAL_ERROR", "message": f"Internal server error: {str(e)}"}
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify the text embedding service is running.
    """
    return {"status": "healthy", "service": "Text Embedding Service API"}