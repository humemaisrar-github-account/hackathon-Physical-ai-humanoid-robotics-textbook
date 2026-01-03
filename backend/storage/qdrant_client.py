"""
Qdrant client initialization and connection utilities for the RAG pipeline.
"""
from typing import Optional, List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from utils.logging_config import get_logger
from utils.error_handling import handle_qdrant_errors, retry_qdrant
from config.config import config
from models.data_models import QdrantRecord

logger = get_logger("qdrant_client")


class QdrantClientWrapper:
    """
    Wrapper class for Qdrant client with connection management and utilities.
    """
    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None, collection_name: Optional[str] = None):
        """
        Initialize the Qdrant client wrapper.

        Args:
            url: Qdrant URL (defaults to config value)
            api_key: Qdrant API key (defaults to config value)
            collection_name: Collection name (defaults to config value)
        """
        self.url = url or config.qdrant_url
        self.api_key = api_key or config.qdrant_api_key
        self.collection_name = collection_name or config.qdrant_collection_name
        self.client = self._initialize_client()
        self._collection_initialized = False

    def _initialize_client(self) -> QdrantClient:
        """
        Initialize the Qdrant client based on configuration.

        Returns:
            QdrantClient: Initialized client instance
        """
        try:
            if self.url.startswith('http'):
                # Cloud instance
                client = QdrantClient(
                    url=self.url,
                    api_key=self.api_key,
                    prefer_grpc=True  # Use gRPC for better performance if available
                )
            else:
                # Local instance
                client = QdrantClient(host=self.url, prefer_grpc=True)

            logger.info(f"Qdrant client initialized for collection: {self.collection_name}")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {str(e)}")
            raise

    @handle_qdrant_errors
    def ensure_collection_exists(
        self,
        vector_size: int = 1024,  # Default size for Cohere embeddings
        distance_metric: models.Distance = models.Distance.COSINE
    ) -> bool:
        """
        Ensure the collection exists, create it if it doesn't.

        Args:
            vector_size: Size of the embedding vectors
            distance_metric: Distance metric for similarity search

        Returns:
            bool: True if collection exists or was created successfully
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_exists = any(col.name == self.collection_name for col in collections.collections)

            if not collection_exists:
                # Create collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=distance_metric
                    ),
                    # Enable payload indexing for metadata fields
                    optimizers_config=models.OptimizersConfigDiff(
                        memmap_threshold=20000,  # Use memory mapping for larger collections
                        indexing_threshold=20000  # Index vectors in memory up to this threshold
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Qdrant collection already exists: {self.collection_name}")

            self._collection_initialized = True
            return True
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {str(e)}")
            raise

    @handle_qdrant_errors
    @retry_qdrant
    def upsert_vectors(
        self,
        records: List[QdrantRecord],
        batch_size: Optional[int] = None
    ) -> bool:
        """
        Upsert (insert or update) vectors to the Qdrant collection.

        Args:
            records: List of QdrantRecord objects to store
            batch_size: Number of records to process in each batch (defaults to config)

        Returns:
            bool: True if successful
        """
        if not records:
            logger.warning("No records to upsert")
            return True

        batch_size = batch_size or config.batch_size_qdrant
        total_records = len(records)
        logger.info(f"Upserting {total_records} vectors to collection {self.collection_name}")

        # Convert QdrantRecord objects to Qdrant PointStruct objects
        points = []
        for record in records:
            point = models.PointStruct(
                id=record.id,
                vector=record.vector,
                payload=record.payload
            )
            points.append(point)

        # Process in batches
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            try:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                logger.debug(f"Upserted batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
            except Exception as e:
                logger.error(f"Error upserting batch {i//batch_size + 1}: {str(e)}")
                raise

        logger.info(f"Successfully upserted {total_records} vectors")
        return True

    @handle_qdrant_errors
    @retry_qdrant
    def search_vectors(
        self,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[models.Filter] = None,
        with_payload: bool = True,
        with_vectors: bool = False
    ) -> List[models.ScoredPoint]:
        """
        Search for similar vectors in the collection.

        Args:
            query_vector: The vector to search for similar ones
            limit: Maximum number of results to return
            filters: Optional filters to apply to the search
            with_payload: Whether to return payload data
            with_vectors: Whether to return vector data

        Returns:
            List[models.ScoredPoint]: List of similar vectors with scores
        """
        try:
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
                prefetch=[],
                with_payload=with_payload,
                with_vectors=with_vectors,
                query_filter=filters
                )
            results = response.points or []
            logger.debug(f"Search returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error searching vectors: {str(e)}")
            raise

    @handle_qdrant_errors
    @retry_qdrant
    def get_vector_count(self) -> int:
        """
        Get the total count of vectors in the collection.

        Returns:
            int: Number of vectors in the collection
        """
        try:
            count = self.client.count(
                collection_name=self.collection_name
            )
            logger.info(f"Collection {self.collection_name} contains {count.count} vectors")
            return count.count
        except Exception as e:
            logger.error(f"Error getting vector count: {str(e)}")
            raise

    @handle_qdrant_errors
    @retry_qdrant
    def delete_vectors_by_ids(self, ids: List[str]) -> bool:
        """
        Delete vectors from the collection by their IDs.

        Args:
            ids: List of vector IDs to delete

        Returns:
            bool: True if successful
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=ids
                )
            )
            logger.info(f"Deleted {len(ids)} vectors from collection")
            return True
        except Exception as e:
            logger.error(f"Error deleting vectors: {str(e)}")
            raise

    @handle_qdrant_errors
    @retry_qdrant
    def get_vectors_by_ids(self, ids: List[str]) -> List[models.Record]:
        """
        Retrieve vectors from the collection by their IDs.

        Args:
            ids: List of vector IDs to retrieve

        Returns:
            List[models.Record]: List of vector records
        """
        try:
            records = self.client.retrieve(
                collection_name=self.collection_name,
                ids=ids,
                with_payload=True,
                with_vectors=True
            )
            logger.debug(f"Retrieved {len(records)} vectors by IDs")
            return records
        except Exception as e:
            logger.error(f"Error retrieving vectors by IDs: {str(e)}")
            raise

    @handle_qdrant_errors
    @retry_qdrant
    def filter_vectors(
        self,
        conditions: List[models.Condition],
        limit: int = 100,
        offset: int = 0
    ) -> List[models.Record]:
        """
        Filter vectors based on conditions.

        Args:
            conditions: List of filter conditions
            limit: Maximum number of results to return
            offset: Offset for pagination

        Returns:
            List[models.Record]: List of matching vector records
        """
        try:
            filter_model = models.Filter(must=conditions)
            records = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_model,
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=True
            )
            logger.debug(f"Filter returned {len(records[0])} vectors")
            return records[0]  # scroll returns (records, next_offset)
        except Exception as e:
            logger.error(f"Error filtering vectors: {str(e)}")
            raise

    def health_check(self) -> bool:
        """
        Check if the Qdrant client is healthy and can connect.

        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            # Try to get collections as a simple health check
            self.client.get_collections()
            logger.info("Qdrant health check passed")
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {str(e)}")
            return False


# Global Qdrant client instance
qdrant_client = None


def get_qdrant_client() -> QdrantClientWrapper:
    """
    Get the global Qdrant client instance, creating it if it doesn't exist.

    Returns:
        QdrantClientWrapper: The Qdrant client wrapper instance
    """
    global qdrant_client
    if qdrant_client is None:
        qdrant_client = QdrantClientWrapper()
    return qdrant_client


def initialize_qdrant_collection(
    collection_name: Optional[str] = None,
    vector_size: int = 1024,
    distance_metric: models.Distance = models.Distance.COSINE
) -> bool:
    """
    Initialize the Qdrant collection with the specified parameters.

    Args:
        collection_name: Name of the collection (uses config default if None)
        vector_size: Size of the embedding vectors
        distance_metric: Distance metric for similarity search

    Returns:
        bool: True if initialization was successful
    """
    client = get_qdrant_client()
    if collection_name:
        # If a specific collection name is provided, we need a new client instance
        temp_client = QdrantClientWrapper(collection_name=collection_name)
        return temp_client.ensure_collection_exists(vector_size, distance_metric)
    else:
        return client.ensure_collection_exists(vector_size, distance_metric)


def store_embeddings_in_qdrant(
    records: List[QdrantRecord],
    batch_size: Optional[int] = None
) -> bool:
    """
    Store embedding records in Qdrant.

    Args:
        records: List of QdrantRecord objects to store
        batch_size: Number of records to process in each batch

    Returns:
        bool: True if storage was successful
    """
    client = get_qdrant_client()
    return client.upsert_vectors(records, batch_size)


def search_similar_content(
    query_vector: List[float],
    limit: int = 10,
    filters: Optional[models.Filter] = None
) -> List[models.ScoredPoint]:
    """
    Search for similar content in the Qdrant collection.

    Args:
        query_vector: The vector to search for similar ones
        limit: Maximum number of results to return
        filters: Optional filters to apply to the search

    Returns:
        List[models.ScoredPoint]: List of similar vectors with scores
    """
    client = get_qdrant_client()
    return client.search_vectors(query_vector, limit, filters)


def get_embedding_count() -> int:
    """
    Get the total count of embeddings in the collection.

    Returns:
        int: Number of embeddings in the collection
    """
    client = get_qdrant_client()
    return client.get_vector_count()


if __name__ == "__main__":
    # Test the Qdrant client utilities
    print("Testing Qdrant client utilities...")

    # Create a mock QdrantRecord for testing
    from datetime import datetime
    test_record = QdrantRecord(
        id="test_chunk_001",
        vector=[0.1, 0.2, 0.3, 0.4, 0.5] * 205,  # Make it 1025-dimensions to match Cohere
        payload={
            "page_url": "https://test.com/page1",
            "heading_path": "Chapter 1 > Section A",
            "content_raw": "This is a test content chunk for validation",
            "chunk_id": "test_chunk_001",
            "token_count": 350,
            "position_in_page": 0
        },
        created_at=datetime.now()
    )

    # Initialize client
    try:
        client = get_qdrant_client()
        print("Qdrant client initialized successfully")

        # Health check
        is_healthy = client.health_check()
        print(f"Qdrant health check: {'PASSED' if is_healthy else 'FAILED'}")

        # Test collection initialization (this will create the collection if it doesn't exist)
        collection_ok = initialize_qdrant_collection()
        print(f"Collection initialization: {'SUCCESS' if collection_ok else 'FAILED'}")

        # Test storing embeddings (commented out to avoid actually storing during test)
        # store_ok = store_embeddings_in_qdrant([test_record])
        # print(f"Embedding storage test: {'SUCCESS' if store_ok else 'FAILED'}")

        # Test getting count
        count = get_embedding_count()
        print(f"Current embedding count: {count}")

    except Exception as e:
        print(f"Error during Qdrant client test: {e}")