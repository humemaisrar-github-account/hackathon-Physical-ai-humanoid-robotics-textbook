import logging
from typing import Optional, Dict, Any, List
from qdrant_client import QdrantClient
from qdrant_client.http import models
from src.lib.config import Config


class QdrantService:
    """
    Service class to manage Qdrant client connection and operations.
    """

    def __init__(self):
        """
        Initialize Qdrant client with configuration from environment variables.
        """
        self.client = QdrantClient(
            url=Config.QDRANT_HOST,
            api_key=Config.QDRANT_API_KEY,
            prefer_grpc=False,
        )
        self.collection_name = Config.QDRANT_COLLECTION_NAME

    # ------------------------------------------------------------------
    # Connection & Health
    # ------------------------------------------------------------------

    def connect_to_qdrant(self) -> bool:
        """
        Test connection to Qdrant server.
        """
        try:
            self.client.get_collection(self.collection_name)
            logging.info(
                f"Successfully connected to Qdrant collection: {self.collection_name}"
            )
            return True
        except Exception as e:
            logging.error(f"Failed to connect to Qdrant: {str(e)}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Qdrant connection.
        """
        try:
            health = self.client.health()
            return {
                "status": "healthy",
                "health_info": health,
                "collection_exists": self.collection_exists(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "collection_exists": False,
            }

    def collection_exists(self) -> bool:
        """
        Check if the configured collection exists.
        """
        try:
            self.client.get_collection(self.collection_name)
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Vector Search (FIXED)
    # ------------------------------------------------------------------

    def search_vectors(
        self,
        vector: List[float],
        top_k: int = 3,
        filters: Optional[Dict[str, Any]] = None,
    ):
        """
        Search for similar vectors in the collection.

        Returns:
            List[ScoredPoint]  (ALWAYS normalized)
        """
        try:
            qdrant_filters = None

            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        models.FieldCondition(
                            key=f"metadata.{key}",
                            match=models.MatchValue(value=value),
                        )
                    )

                if conditions:
                    qdrant_filters = models.Filter(must=conditions)

            response = self.client.query_points(
                collection_name=self.collection_name,
                query=vector,
                limit=top_k,
                query_filter=qdrant_filters,
                with_payload=True,
                with_vectors=False,
            )

            # ✅ CRITICAL FIX: normalize response across versions
            points = response.points if hasattr(response, "points") else response[0]

            return points

        except Exception as e:
            logging.error(f"Error during vector search: {str(e)}")
            raise
