"""
Retrieval service for the RAG Agent system.
"""

import logging
from typing import List
from qdrant_client import QdrantClient
from src.config.settings import settings
from src.models.agent import RetrievedDocument
from src.services.embedding import EmbeddingService


class RetrievalService:
    """
    Service class for retrieving documents from Qdrant based on semantic similarity.
    """

    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            prefer_grpc=False,
        )

        self.collection_name = (
            settings.qdrant_collection_name
            or settings.qdrant_collection
            or "book_content_chunks"
        )

        self.logger = logging.getLogger(__name__)

    # ---------------------------------------------------------

    def _normalize_points(self, response):
        """
        Normalize Qdrant query response across client versions.
        """
        if hasattr(response, "points"):
            return response.points
        if isinstance(response, tuple):
            return response[0]
        return response

    # ---------------------------------------------------------

    def retrieve_documents(self, query: str, top_k: int = 5) -> List[RetrievedDocument]:
        self.logger.info(
            f"Starting document retrieval for query: {query[:50]}..., top_k: {top_k}"
        )

        query_embedding = self.embedding_service.embed_text(query)

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )

        points = self._normalize_points(response)

        retrieved_docs: List[RetrievedDocument] = []

        for i, point in enumerate(points):
            payload = point.payload or {}

            # Extract content from either the 'content' field or 'content_raw' in metadata
            content = payload.get("content", "")
            if not content and "content_raw" in payload:
                content = payload["content_raw"]
            elif not content and isinstance(payload.get("metadata"), dict) and "content_raw" in payload["metadata"]:
                content = payload["metadata"]["content_raw"]

            retrieved_docs.append(
                RetrievedDocument(
                    id=str(point.id),
                    content=content,
                    metadata={k: v for k, v in payload.items() if k != "content"},
                    score=float(point.score),
                )
            )

            self.logger.debug(
                f"Retrieved source {i+1}: ID={point.id}, "
                f"Score={point.score:.3f}, "
                f"Content preview={payload.get('content','')[:100]}..."
            )

        return retrieved_docs

    # ---------------------------------------------------------

    def retrieve_documents_by_embedding(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[RetrievedDocument]:

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )

        points = self._normalize_points(response)

        retrieved_docs: List[RetrievedDocument] = []

        for point in points:
            payload = point.payload or {}

            # Extract content from either the 'content' field or 'content_raw' in metadata
            content = payload.get("content", "")
            if not content and "content_raw" in payload:
                content = payload["content_raw"]
            elif not content and isinstance(payload.get("metadata"), dict) and "content_raw" in payload["metadata"]:
                content = payload["metadata"]["content_raw"]

            retrieved_docs.append(
                RetrievedDocument(
                    id=str(point.id),
                    content=content,
                    metadata={k: v for k, v in payload.items() if k != "content"},
                    score=float(point.score),
                )
            )

        return retrieved_docs
