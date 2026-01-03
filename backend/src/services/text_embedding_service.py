"""
Text Embedding Service for converting text to embeddings and managing Qdrant storage.

This module provides functionality to:
1. Convert text to embeddings using Cohere
2. Save embeddings to Qdrant with appropriate IDs and metadata
3. Retrieve relevant embeddings from Qdrant based on similarity search
"""
import logging
from typing import List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime

import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models

from src.config.settings import settings


class TextEmbeddingService:
    """
    Service class for handling text embeddings and Qdrant operations.
    """

    def __init__(self):
        """
        Initialize the text embedding service with Cohere and Qdrant clients.
        """
        # Initialize Cohere client for embeddings
        self.cohere_client = cohere.Client(settings.cohere_api_key)

        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            prefer_grpc=False,
        )

        # Set collection name
        self.collection_name = (
            settings.qdrant_collection_name
            or settings.qdrant_collection
            or "text_embeddings"
        )

        # Set up logging
        self.logger = logging.getLogger(__name__)

    def _ensure_collection_exists(self, vector_size: int = 1024) -> bool:
        """
        Ensure the Qdrant collection exists, create it if it doesn't.

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
                # Create collection with specified vector size
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE
                    ),
                )
                self.logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                self.logger.info(f"Qdrant collection already exists: {self.collection_name}")

            return True
        except Exception as e:
            self.logger.error(f"Error ensuring collection exists: {str(e)}")
            return False

    def convert_text_to_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Convert a list of texts to embeddings using Cohere.

        Args:
            texts: List of text strings to convert to embeddings

        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        if not texts:
            self.logger.warning("No texts provided for embedding")
            return []

        try:
            self.logger.info(f"Generating embeddings for {len(texts)} texts")

            response = self.cohere_client.embed(
                texts=texts,
                model="embed-english-v3.0",
                input_type="search_document"  # Using search_document for document chunks
            )

            embeddings = response.embeddings
            self.logger.info(f"Successfully generated {len(embeddings)} embeddings")

            return embeddings
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {str(e)}")
            raise

    def convert_single_text_to_embedding(self, text: str) -> List[float]:
        """
        Convert a single text to embedding using Cohere.

        Args:
            text: Text string to convert to embedding

        Returns:
            Embedding vector (list of floats)
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            self.logger.info("Generating embedding for single text")

            response = self.cohere_client.embed(
                texts=[text],
                model="embed-english-v3.0",
                input_type="search_query"  # Using search_query for query texts
            )

            embedding = response.embeddings[0]
            self.logger.info("Successfully generated embedding for single text")

            return embedding
        except Exception as e:
            self.logger.error(f"Error generating embedding for single text: {str(e)}")
            raise

    def save_embeddings_to_qdrant(
        self,
        texts: List[str],
        metadata_list: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Save text embeddings to Qdrant with appropriate IDs and metadata.

        Args:
            texts: List of text strings to embed and save
            metadata_list: Optional list of metadata dictionaries for each text
            ids: Optional list of IDs for each text (if not provided, UUIDs will be generated)

        Returns:
            List of IDs used for the saved embeddings
        """
        if not texts:
            self.logger.warning("No texts provided to save")
            return []

        # Generate embeddings
        embeddings = self.convert_text_to_embeddings(texts)

        # Ensure collection exists
        collection_ok = self._ensure_collection_exists()
        if not collection_ok:
            raise Exception("Failed to ensure Qdrant collection exists")

        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid4()) for _ in range(len(texts))]
        elif len(ids) != len(texts):
            raise ValueError("Number of IDs must match number of texts")

        # Prepare metadata if not provided
        if metadata_list is None:
            metadata_list = [{} for _ in range(len(texts))]
        elif len(metadata_list) != len(texts):
            raise ValueError("Number of metadata entries must match number of texts")

        # Add default metadata fields
        for i, meta in enumerate(metadata_list):
            meta.setdefault("text", texts[i])
            meta.setdefault("created_at", datetime.now().isoformat())
            meta.setdefault("id", ids[i])

        # Prepare points for Qdrant
        points = []
        for text_id, embedding, metadata in zip(ids, embeddings, metadata_list):
            point = models.PointStruct(
                id=text_id,
                vector=embedding,
                payload=metadata
            )
            points.append(point)

        # Save to Qdrant
        try:
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            self.logger.info(f"Successfully saved {len(points)} embeddings to Qdrant")
            return ids
        except Exception as e:
            self.logger.error(f"Error saving embeddings to Qdrant: {str(e)}")
            raise

    def retrieve_similar_embeddings(
        self,
        query_text: str,
        top_k: int = 5,
        filters: Optional[models.Filter] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the most similar embeddings from Qdrant based on a query text.

        Args:
            query_text: Text to search for similar embeddings
            top_k: Number of similar embeddings to retrieve (default 5)
            filters: Optional filters to apply to the search

        Returns:
            List of dictionaries containing the similar embeddings and their metadata
        """
        if not query_text or not query_text.strip():
            raise ValueError("Query text cannot be empty")

        try:
            # Generate embedding for the query text
            query_embedding = self.convert_single_text_to_embedding(query_text)

            # Search in Qdrant
            results = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=top_k,
                query_filter=filters,
                with_payload=True,
                with_vectors=False,
            )

            # Process results
            similar_embeddings = []
            for point in results.points:
                result = {
                    "id": str(point.id),
                    "score": float(point.score),
                    "payload": point.payload or {},
                    "text": point.payload.get("text", "") if point.payload else ""
                }
                similar_embeddings.append(result)

            self.logger.info(f"Retrieved {len(similar_embeddings)} similar embeddings for query")
            return similar_embeddings
        except Exception as e:
            self.logger.error(f"Error retrieving similar embeddings: {str(e)}")
            raise

    def get_embedding_count(self) -> int:
        """
        Get the total count of embeddings in the collection.

        Returns:
            Number of embeddings in the collection
        """
        try:
            count_result = self.qdrant_client.count(
                collection_name=self.collection_name
            )
            return count_result.count
        except Exception as e:
            self.logger.error(f"Error getting embedding count: {str(e)}")
            raise

    def delete_embeddings_by_ids(self, ids: List[str]) -> bool:
        """
        Delete embeddings from Qdrant by their IDs.

        Args:
            ids: List of IDs to delete

        Returns:
            True if deletion was successful
        """
        try:
            self.qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=ids)
            )
            self.logger.info(f"Successfully deleted {len(ids)} embeddings from Qdrant")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting embeddings: {str(e)}")
            raise


def create_text_embedding_service() -> TextEmbeddingService:
    """
    Factory function to create a TextEmbeddingService instance.

    Returns:
        Configured TextEmbeddingService instance
    """
    return TextEmbeddingService()


# Example usage and testing
if __name__ == "__main__":
    # Create the service
    service = create_text_embedding_service()

    # Example texts to embed
    sample_texts = [
        "The quick brown fox jumps over the lazy dog",
        "Machine learning is a subset of artificial intelligence",
        "Python is a popular programming language for data science",
        "Natural language processing enables computers to understand human language",
        "Vector databases like Qdrant are essential for semantic search"
    ]

    # Example metadata for each text
    sample_metadata = [
        {"category": "animals", "source": "example1"},
        {"category": "technology", "source": "example2"},
        {"category": "programming", "source": "example3"},
        {"category": "ai", "source": "example4"},
        {"category": "databases", "source": "example5"}
    ]

    print("Testing Text Embedding Service...")

    try:
        # Test embedding conversion
        print("\n1. Converting texts to embeddings...")
        embeddings = service.convert_text_to_embeddings(sample_texts)
        print(f"Generated {len(embeddings)} embeddings with dimension {len(embeddings[0]) if embeddings else 0}")

        # Test saving embeddings to Qdrant
        print("\n2. Saving embeddings to Qdrant...")
        saved_ids = service.save_embeddings_to_qdrant(sample_texts, sample_metadata)
        print(f"Saved {len(saved_ids)} embeddings with IDs: {saved_ids[:3]}...")  # Show first 3 IDs

        # Get count
        count = service.get_embedding_count()
        print(f"Total embeddings in collection: {count}")

        # Test similarity search
        print("\n3. Testing similarity search...")
        query = "artificial intelligence and machine learning"
        similar_results = service.retrieve_similar_embeddings(query, top_k=3)

        print(f"Query: '{query}'")
        print(f"Found {len(similar_results)} similar embeddings:")
        for i, result in enumerate(similar_results, 1):
            print(f"  {i}. Score: {result['score']:.3f}, Text: '{result['text'][:50]}...'")
            print(f"     Metadata: {result['payload']}")

        print("\n✓ Text Embedding Service tests completed successfully!")

    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()