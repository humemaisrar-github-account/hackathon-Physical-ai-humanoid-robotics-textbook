"""
Correct Qdrant Integration for Text Embeddings using Cohere

This module implements a correct Qdrant integration that meets all mandatory requirements:
1. Explicit collection checking and creation on startup
2. Proper QdrantClient initialization with URL and API key
3. Save embeddings function using upsert()
4. Retrieve embeddings function using search()
5. Comprehensive logging
6. Health check endpoint
7. Loud failure handling
"""
import logging
from typing import List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime

import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse

from src.config.settings import settings


class QdrantEmbeddingService:
    """
    Service class for handling text embeddings with correct Qdrant integration.
    """

    def __init__(self):
        """
        Initialize the service with Cohere and Qdrant clients.
        Explicitly check and create collection if needed.
        """
        # Initialize Cohere client for embeddings
        self.cohere_client = cohere.Client(settings.cohere_api_key)

        # Initialize Qdrant client with URL and API key
        self.qdrant_client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            prefer_grpc=False,
        )

        # Set collection name to text_embeddings as required
        self.collection_name = "text_embeddings"

        # Set up logging
        self.logger = logging.getLogger(__name__)

        # On startup, explicitly check if collection exists and create if needed
        self._ensure_collection_exists()

    def _ensure_collection_exists(self, vector_size: int = 1024) -> bool:
        """
        On service startup, explicitly check if the Qdrant collection exists.
        If it does NOT exist, create it with required parameters.

        Args:
            vector_size: Size of the embedding vectors (default 1024 for Cohere)

        Returns:
            True if collection exists or was created successfully
        """
        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections()
            collection_exists = any(col.name == self.collection_name for col in collections.collections)

            if not collection_exists:
                # Create collection with required parameters
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE  # Required: COSINE distance
                    ),
                )
                self.logger.info(f"Created Qdrant collection: {self.collection_name} with vector_size={vector_size}, distance=COSINE")
            else:
                self.logger.info(f"Qdrant collection already exists: {self.collection_name}")

            return True
        except Exception as e:
            self.logger.error(f"CRITICAL: Error ensuring collection exists: {str(e)}")
            raise  # Fail loudly as required

    def save_embeddings(self, texts: List[str], metadata_list: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Implement a save_embeddings function that:
        - Generates embeddings using Cohere embed-english-v3.0
        - Uses client.upsert() to store vectors
        - Stores metadata payload correctly
        - Logs successful upserts with vector IDs
        - Raises explicit errors on failure

        Args:
            texts: List of text strings to embed and save
            metadata_list: Optional list of metadata dictionaries for each text

        Returns:
            List of IDs used for the saved embeddings
        """
        if not texts:
            self.logger.warning("WARNING: No texts provided to save")
            return []

        try:
            # Generate embeddings using Cohere embed-english-v3.0
            self.logger.info(f"Generating embeddings for {len(texts)} texts using Cohere embed-english-v3.0")
            response = self.cohere_client.embed(
                texts=texts,
                model="embed-english-v3.0",  # Required: embed-english-v3.0
                input_type="search_document"
            )
            embeddings = response.embeddings
            self.logger.info(f"Successfully generated {len(embeddings)} embeddings")

            # Generate unique IDs for each text
            ids = [str(uuid4()) for _ in range(len(texts))]

            # Prepare metadata if not provided
            if metadata_list is None:
                metadata_list = [{} for _ in range(len(texts))]
            elif len(metadata_list) != len(texts):
                raise ValueError(f"Number of metadata entries ({len(metadata_list)}) must match number of texts ({len(texts)})")

            # Add default metadata fields
            for i, meta in enumerate(metadata_list):
                meta.setdefault("text", texts[i])
                meta.setdefault("created_at", datetime.now().isoformat())
                meta.setdefault("id", ids[i])

            # Prepare points for Qdrant upsert
            points = []
            for text_id, embedding, metadata in zip(ids, embeddings, metadata_list):
                point = models.PointStruct(
                    id=text_id,
                    vector=embedding,
                    payload=metadata
                )
                points.append(point)

            # Use client.upsert() to store vectors (required)
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            # Log successful upserts with vector IDs
            self.logger.info(f"SUCCESS: Upserted {len(points)} embeddings to Qdrant collection '{self.collection_name}' with IDs: {ids}")

            return ids

        except Exception as e:
            self.logger.error(f"CRITICAL: Error saving embeddings to Qdrant: {str(e)}")
            raise  # Fail loudly as required

    def retrieve_embeddings(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Implement a retrieve_embeddings function that:
        - Accepts a text query
        - Converts it to an embedding
        - Performs similarity search using client.search()
        - Returns top-k results with payloads and scores

        Args:
            query_text: Text to search for similar embeddings
            top_k: Number of similar embeddings to retrieve (default 5)

        Returns:
            List of dictionaries containing the similar embeddings with payloads and scores
        """
        if not query_text or not query_text.strip():
            raise ValueError("Query text cannot be empty")

        try:
            # Convert query text to embedding using Cohere
            self.logger.info(f"Converting query text to embedding: '{query_text[:50]}...'")
            response = self.cohere_client.embed(
                texts=[query_text],
                model="embed-english-v3.0",  # Required: embed-english-v3.0
                input_type="search_query"
            )
            query_embedding = response.embeddings[0]
            self.logger.info(f"Successfully generated query embedding")

            # Perform similarity search using client.search() (required)
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                with_payload=True,
                with_vectors=False,
            )

            # Process results and return with payloads and scores
            results = []
            for point in search_results:
                result = {
                    "id": str(point.id),
                    "score": float(point.score),
                    "payload": point.payload or {},
                    "text": point.payload.get("text", "") if point.payload else ""
                }
                results.append(result)

            self.logger.info(f"SUCCESS: Found {len(results)} similar embeddings for query '{query_text[:50]}...'")
            return results

        except Exception as e:
            self.logger.error(f"CRITICAL: Error retrieving embeddings from Qdrant: {str(e)}")
            raise  # Fail loudly as required

    def health_check(self) -> Dict[str, Any]:
        """
        Health check endpoint that verifies:
        - Qdrant connection
        - Collection availability

        Returns:
            Dictionary with health status
        """
        try:
            # Test Qdrant connection by getting collections
            collections = self.qdrant_client.get_collections()
            collection_exists = any(col.name == self.collection_name for col in collections.collections)

            if not collection_exists:
                self.logger.warning(f"HEALTH WARNING: Collection {self.collection_name} does not exist")
                return {
                    "status": "unhealthy",
                    "connection": "ok",
                    "collection": "missing",
                    "message": f"Collection {self.collection_name} does not exist"
                }

            # Test collection by getting count
            count = self.qdrant_client.count(collection_name=self.collection_name)

            self.logger.info(f"HEALTH CHECK: Qdrant connection OK, collection exists with {count.count} vectors")
            return {
                "status": "healthy",
                "connection": "ok",
                "collection": "available",
                "vector_count": count.count
            }

        except Exception as e:
            self.logger.error(f"HEALTH CHECK FAILED: {str(e)}")
            return {
                "status": "unhealthy",
                "connection": "failed",
                "error": str(e)
            }


def create_qdrant_embedding_service() -> QdrantEmbeddingService:
    """
    Factory function to create a QdrantEmbeddingService instance.

    Returns:
        Configured QdrantEmbeddingService instance
    """
    return QdrantEmbeddingService()


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    print("Testing Correct Qdrant Integration...")
    print("=" * 50)

    try:
        # Create the service (this will check/create collection on startup)
        service = create_qdrant_embedding_service()
        print("✓ Service initialized with correct Qdrant integration")

        # Test health check
        print("\n1. Testing health check...")
        health_status = service.health_check()
        print(f"   Health status: {health_status['status']}")
        print(f"   Connection: {health_status['connection']}")
        if 'vector_count' in health_status:
            print(f"   Vector count: {health_status['vector_count']}")

        # Test saving one sample text
        print("\n2. Testing save_embeddings with one sample text...")
        sample_texts = ["This is a sample text for testing Qdrant integration"]
        sample_metadata = [{"category": "test", "source": "integration_test"}]

        saved_ids = service.save_embeddings(sample_texts, sample_metadata)
        print(f"   ✓ Saved embedding with ID: {saved_ids[0]}")

        # Verify the collection now has data
        health_after_save = service.health_check()
        print(f"   Collection now has {health_after_save.get('vector_count', 0)} vectors")

        # Test retrieving via similarity search
        print("\n3. Testing retrieve_embeddings via similarity search...")
        query = "sample text for testing"
        results = service.retrieve_embeddings(query, top_k=1)

        print(f"   ✓ Found {len(results)} similar embeddings")
        if results:
            result = results[0]
            print(f"   ID: {result['id']}")
            print(f"   Score: {result['score']:.3f}")
            print(f"   Text: '{result['text'][:50]}...'")
            print(f"   Payload: {result['payload']}")

        print("\n" + "=" * 50)
        print("✅ ALL MANDATORY REQUIREMENTS MET:")
        print("✓ Collection checked/created on startup")
        print("✓ QdrantClient with URL and API key")
        print("✓ save_embeddings using upsert()")
        print("✓ retrieve_embeddings using search()")
        print("✓ Comprehensive logging")
        print("✓ Health check endpoint")
        print("✓ Loud failure handling")
        print("\nThe collection is now visible in the Qdrant dashboard!")

    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()