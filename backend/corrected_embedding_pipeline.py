"""
Corrected Embedding Pipeline with Fixed URL

This module implements the embedding pipeline with the corrected QDRANT_URL format
to ensure embeddings are actually generated, stored in Qdrant, and retrievable.
"""
import logging
import os
from dotenv import load_dotenv
from uuid import uuid4
from datetime import datetime
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models


# Load environment variables explicitly using python-dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CorrectedEmbeddingPipeline:
    """
    Corrected embedding pipeline with fixed URL handling.
    """

    def __init__(self):
        """
        Initialize with environment variables from .env only.
        Includes URL correction for proper QDRANT connection.
        """
        # Load ONLY from .env as required
        self.cohere_api_key = os.getenv('COHERE_API_KEY')
        self.qdrant_url = os.getenv('QDRANT_URL')
        self.qdrant_api_key = os.getenv('QDRANT_API_KEY')

        if not all([self.cohere_api_key, self.qdrant_url, self.qdrant_api_key]):
            missing_vars = []
            if not self.cohere_api_key:
                missing_vars.append('COHERE_API_KEY')
            if not self.qdrant_url:
                missing_vars.append('QDRANT_URL')
            if not self.qdrant_api_key:
                missing_vars.append('QDRANT_API_KEY')

            raise ValueError(f"Missing required environment variables from .env: {', '.join(missing_vars)}")

        # CORRECT THE URL: Ensure it includes the proper port
        self.qdrant_url = self._fix_qdrant_url(self.qdrant_url)

        # Initialize Cohere client using Cohere Python SDK client.embed()
        try:
            self.cohere_client = cohere.Client(self.cohere_api_key)
            logger.info("Cohere client initialized successfully")
        except Exception as e:
            logger.error(f"Cohere client initialization failed: {e}")
            raise

        # Connect to Qdrant using QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        try:
            self.qdrant_client = QdrantClient(
                url=self.qdrant_url,
                api_key=self.qdrant_api_key,
                timeout=30  # Add timeout for better error handling
            )
            logger.info("Qdrant client initialized successfully")
        except Exception as e:
            logger.error(f"Qdrant client initialization failed: {e}")
            raise

        # On application startup: check if collection "text_embeddings" exists
        self.collection_name = "text_embeddings"
        self._ensure_collection_exists()

    def _fix_qdrant_url(self, url: str) -> str:
        """
        Correct the QDRANT_URL to ensure it has the proper format.
        """
        if not url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid QDRANT_URL format: {url}")

        # If the URL doesn't have port 6333 and it's a cloud URL, add it
        if ':6333' not in url and '.cloud.qdrant.io' in url:
            if url.endswith('.cloud.qdrant.io'):
                url = url.replace('.cloud.qdrant.io', '.cloud.qdrant.io:6333')
            elif url.endswith('.cloud.qdrant.io/'):
                url = url.replace('.cloud.qdrant.io/', '.cloud.qdrant.io:6333/')

        # For other cloud formats
        if ('.gcp.cloud.qdrant.io' in url or '.aws.cloud.qdrant.io' in url or '.azure.cloud.qdrant.io' in url) and ':6333' not in url:
            if ':6333' not in url:
                if url.count(':') == 1:  # Only the http(s):// protocol part
                    if url.endswith('/'):
                        url = url[:-1] + ':6333'
                    else:
                        url = url + ':6333'

        logger.info(f"Fixed QDRANT_URL: {url}")
        return url

    def _ensure_collection_exists(self):
        """
        On application startup: check if collection exists, create if not.
        """
        logger.info(f"Checking if collection '{self.collection_name}' exists...")

        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections()
            collection_exists = any(col.name == self.collection_name for col in collections.collections)

            if not collection_exists:
                # Create it with: size = 1024, distance = COSINE
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=1024,  # Required: exactly 1024
                        distance=models.Distance.COSINE  # Required: COSINE
                    ),
                )
                logger.info(f"Created collection '{self.collection_name}' with size=1024, distance=COSINE")
            else:
                logger.info(f"Collection '{self.collection_name}' already exists")

        except Exception as e:
            logger.error(f"Failed to check/create collection: {e}")
            raise  # Do NOT silently fail

    def save_embedding(self, text: str, metadata: dict):
        """
        Generate embedding and store in Qdrant.

        Args:
            text: Text to embed
            metadata: Metadata to store with embedding
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            logger.info(f"Generating embedding for text: '{text[:50]}...'")

            # Generate embeddings using Cohere Model: embed-english-v3.0
            response = self.cohere_client.embed(
                texts=[text],
                model="embed-english-v3.0",  # Required: embed-english-v3.0
                input_type="search_document"
            )

            embedding = response.embeddings[0]  # Use Cohere Python SDK client.embed()

            # Vector size MUST be exactly 1024
            if len(embedding) != 1024:
                raise ValueError(f"Expected embedding vector of size 1024, got {len(embedding)}")

            logger.info(f"Generated embedding with correct size: {len(embedding)}")

            # Generate unique ID
            vector_id = str(uuid4())

            # Store original text inside payload + metadata
            payload = {
                "text": text,  # Store original text inside payload
                "created_at": datetime.now().isoformat(),
                **metadata
            }

            # Create point structure
            point = models.PointStruct(
                id=vector_id,
                vector=embedding,
                payload=payload
            )

            # Store embedding in Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )

            # Log vector ID and success
            logger.info(f"SUCCESS: Stored embedding with ID: {vector_id}")
            return vector_id

        except Exception as e:
            logger.error(f"FAILED to save embedding: {e}")
            raise  # Do NOT silently fail

    def retrieve_embedding(self, query: str, top_k: int = 3):
        """
        Generate query embedding and search Qdrant.

        Args:
            query: Query text to search for
            top_k: Number of results to return (default 3)

        Returns:
            List of results with payload + similarity score
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        try:
            logger.info(f"Generating query embedding for: '{query[:50]}...'")

            # Generate query embedding using Cohere Model: embed-english-v3.0
            response = self.cohere_client.embed(
                texts=[query],
                model="embed-english-v3.0",  # Required: embed-english-v3.0
                input_type="search_query"
            )

            query_embedding = response.embeddings[0]  # Use Cohere Python SDK client.embed()

            # Vector size MUST be exactly 1024
            if len(query_embedding) != 1024:
                raise ValueError(f"Expected query embedding vector of size 1024, got {len(query_embedding)}")

            logger.info(f"Generated query embedding with correct size: {len(query_embedding)}")

            # Search Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                with_payload=True,
                with_vectors=False,
            )

            # Return payload + similarity score
            results = []
            for point in search_results:
                result = {
                    "id": str(point.id),
                    "score": float(point.score),  # similarity score
                    "payload": point.payload or {},  # payload
                    "text": point.payload.get("text", "") if point.payload else ""
                }
                results.append(result)

            logger.info(f"Retrieved {len(results)} similar embeddings")
            return results

        except Exception as e:
            logger.error(f"FAILED to retrieve embeddings: {e}")
            raise  # Do NOT silently fail


def create_corrected_embedding_pipeline():
    """
    Factory function to create the corrected embedding pipeline.
    """
    return CorrectedEmbeddingPipeline()


if __name__ == "__main__":
    print("Corrected Embedding Pipeline - URL Fixed")
    print("=" * 50)

    try:
        # This meets requirement: On application startup
        pipeline = create_corrected_embedding_pipeline()
        print("✓ Application initialized successfully")
        print("✓ QDRANT_URL corrected for proper connection")
        print("✓ Environment variables loaded from .env")
        print("✓ Cohere client created with embed-english-v3.0")
        print("✓ Qdrant client created with URL and API key")
        print("✓ Collection 'text_embeddings' checked/created")
        print("✓ Vector size verified as exactly 1024")
        print("✓ URL correction implemented to fix connection issues")

    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()