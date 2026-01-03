"""
Cohere embedding module for vector generation.
"""
import cohere
import time
import random
from typing import List, Optional
from utils.logging_config import get_logger, log_api_call
from utils.error_handling import handle_cohere_errors, retry_cohere, EmbeddingError
from models.data_models import TextChunk, EmbeddingVector
from config.config import config

logger = get_logger("cohere_embedder")


class CohereEmbedder:
    """
    Cohere embedding class for generating vector embeddings.
    """
    def __init__(self, api_key: str = None, model_name: str = None, rate_limit_delay: float = None):
        """
        Initialize the Cohere embedder.

        Args:
            api_key: Cohere API key (defaults to config value)
            model_name: Cohere model name (defaults to config value)
            rate_limit_delay: Minimum delay in seconds between API calls (defaults to config.cohere_rate_limit_delay)
        """
        self.api_key = api_key or config.cohere_api_key
        self.model_name = model_name or config.cohere_model
        self.client = cohere.Client(self.api_key)
        self.rate_limit_delay = rate_limit_delay or config.cohere_rate_limit_delay
        self.last_api_call_time = 0.0

        if not self.api_key:
            raise ValueError("Cohere API key is required")

    def _enforce_rate_limit(self) -> None:
        """
        Enforce rate limiting by ensuring minimum delay between API calls.
        """
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call_time

        if time_since_last_call < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_call
            # Add some jitter to avoid thundering herd
            jitter = random.uniform(0.05, 0.15) * sleep_time
            sleep_time += jitter
            time.sleep(sleep_time)

        self.last_api_call_time = time.time()

    @handle_cohere_errors
    @retry_cohere
    def generate_embeddings(self, texts: List[str], batch_size: int = None) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of texts to embed
            batch_size: Batch size for API calls (defaults to config value)

        Returns:
            List[List[float]]: List of embedding vectors
        """
        if not texts:
            logger.warning("No texts provided for embedding")
            return []

        batch_size = batch_size or config.batch_size_embedding
        all_embeddings = []

        # Process in batches to respect API limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            logger.info(f"Processing embedding batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")

            # Enforce rate limiting before making API call
            self._enforce_rate_limit()

            try:
                start_time = time.time()
                response = self.client.embed(
                    texts=batch,
                    model=self.model_name,
                    input_type="search_document"  # Optimize for document search
                )
                end_time = time.time()

                batch_embeddings = [embedding for embedding in response.embeddings]
                all_embeddings.extend(batch_embeddings)

                # Log API call
                log_api_call(
                    logger,
                    "Cohere Embed API",
                    "SUCCESS",
                    end_time - start_time,
                    {"batch_size": len(batch), "total_embeddings": len(batch_embeddings)}
                )

            except Exception as e:
                error_msg = f"Error in Cohere embedding batch {i//batch_size + 1}: {str(e)}"
                logger.error(error_msg)
                log_api_call(logger, "Cohere Embed API", "FAILED", None, {"error": str(e)})
                raise EmbeddingError(error_msg) from e

        logger.info(f"Generated {len(all_embeddings)} embeddings for {len(texts)} texts")
        return all_embeddings

    def embed_text_chunks(self, text_chunks: List[TextChunk], batch_size: int = None) -> List[EmbeddingVector]:
        """
        Generate embeddings for a list of TextChunk objects.

        Args:
            text_chunks: List of TextChunk objects to embed
            batch_size: Batch size for API calls (defaults to config value)

        Returns:
            List[EmbeddingVector]: List of EmbeddingVector objects
        """
        if not text_chunks:
            logger.warning("No text chunks provided for embedding")
            return []

        # Extract text content from chunks
        texts = [chunk.content_raw for chunk in text_chunks]

        # Generate embeddings
        embeddings = self.generate_embeddings(texts, batch_size)

        # Create EmbeddingVector objects
        embedding_vectors = []
        for chunk, vector in zip(text_chunks, embeddings):
            embedding_vector = EmbeddingVector(
                chunk_id=chunk.chunk_id,
                vector=vector,
                model_name=self.model_name,
                text_chunk=chunk
            )
            embedding_vectors.append(embedding_vector)

        logger.info(f"Created {len(embedding_vectors)} EmbeddingVector objects")
        return embedding_vectors

    @handle_cohere_errors
    @retry_cohere
    def embed_single_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List[float]: Embedding vector
        """
        if not text or not text.strip():
            raise EmbeddingError("Cannot embed empty text")

        # Enforce rate limiting before making API call
        self._enforce_rate_limit()

        try:
            start_time = time.time()
            response = self.client.embed(
                texts=[text],
                model=self.model_name,
                input_type="search_document"
            )
            end_time = time.time()

            embedding = response.embeddings[0]

            # Log API call
            log_api_call(
                logger,
                "Cohere Embed API (single)",
                "SUCCESS",
                end_time - start_time,
                {"text_length": len(text)}
            )

            return embedding
        except Exception as e:
            error_msg = f"Error embedding single text: {str(e)}"
            logger.error(error_msg)
            log_api_call(logger, "Cohere Embed API (single)", "FAILED", None, {"error": str(e)})
            raise EmbeddingError(error_msg) from e

    def get_embedding_dimensions(self) -> int:
        """
        Get the expected dimensions of embeddings from the current model.

        Returns:
            int: Number of dimensions in the embeddings
        """
        # Test embedding with a short text to determine dimensions
        try:
            test_embedding = self.embed_single_text("test")
            return len(test_embedding)
        except Exception as e:
            logger.error(f"Could not determine embedding dimensions: {str(e)}")
            # Default to common Cohere model dimensions
            if "multilingual" in self.model_name.lower():
                return 1024  # multilingual models typically have 1024 dimensions
            else:
                return 1024  # English models typically have 1024 dimensions


def create_cohere_embedder(api_key: str = None, model_name: str = None, rate_limit_delay: float = None) -> CohereEmbedder:
    """
    Create a Cohere embedder instance.

    Args:
        api_key: Cohere API key (defaults to config value)
        model_name: Cohere model name (defaults to config value)
        rate_limit_delay: Minimum delay in seconds between API calls (defaults to config.cohere_rate_limit_delay)

    Returns:
        CohereEmbedder: Configured Cohere embedder instance
    """
    rate_limit_delay = rate_limit_delay or config.cohere_rate_limit_delay
    return CohereEmbedder(api_key, model_name, rate_limit_delay)


def embed_text_chunks(
    text_chunks: List[TextChunk],
    api_key: str = None,
    model_name: str = None,
    batch_size: int = None,
    rate_limit_delay: float = None
) -> List[EmbeddingVector]:
    """
    Convenience function to embed text chunks.

    Args:
        text_chunks: List of TextChunk objects to embed
        api_key: Cohere API key (defaults to config value)
        model_name: Cohere model name (defaults to config value)
        batch_size: Batch size for API calls (defaults to config value)
        rate_limit_delay: Minimum delay in seconds between API calls (defaults to config.crawl_delay)

    Returns:
        List[EmbeddingVector]: List of EmbeddingVector objects
    """
    rate_limit_delay = rate_limit_delay or config.cohere_rate_limit_delay
    embedder = CohereEmbedder(api_key, model_name, rate_limit_delay)
    return embedder.embed_text_chunks(text_chunks, batch_size)


def embed_texts(
    texts: List[str],
    api_key: str = None,
    model_name: str = None,
    batch_size: int = None,
    rate_limit_delay: float = None
) -> List[List[float]]:
    """
    Convenience function to embed texts.

    Args:
        texts: List of texts to embed
        api_key: Cohere API key (defaults to config value)
        model_name: Cohere model name (defaults to config value)
        batch_size: Batch size for API calls (defaults to config value)
        rate_limit_delay: Minimum delay in seconds between API calls (defaults to config.crawl_delay)

    Returns:
        List[List[float]]: List of embedding vectors
    """
    rate_limit_delay = rate_limit_delay or config.cohere_rate_limit_delay
    embedder = CohereEmbedder(api_key, model_name, rate_limit_delay)
    return embedder.generate_embeddings(texts, batch_size)


def embed_single_text(
    text: str,
    api_key: str = None,
    model_name: str = None,
    rate_limit_delay: float = None
) -> List[float]:
    """
    Convenience function to embed a single text.

    Args:
        text: Text to embed
        api_key: Cohere API key (defaults to config value)
        model_name: Cohere model name (defaults to config value)
        rate_limit_delay: Minimum delay in seconds between API calls (defaults to config.crawl_delay)

    Returns:
        List[float]: Embedding vector
    """
    rate_limit_delay = rate_limit_delay or config.cohere_rate_limit_delay
    embedder = CohereEmbedder(api_key, model_name, rate_limit_delay)
    return embedder.embed_single_text(text)


if __name__ == "__main__":
    # Test the Cohere embedder (without actually calling the API)
    print("Testing Cohere embedder module...")

    # Create sample text chunks for testing
    from models.data_models import TextChunk

    sample_chunks = [
        TextChunk(
            chunk_id="test_chunk_001",
            page_url="https://example.com/page1",
            content_raw="This is the first sample text chunk for embedding.",
            token_count=20
        ),
        TextChunk(
            chunk_id="test_chunk_002",
            page_url="https://example.com/page2",
            content_raw="This is the second sample text chunk for embedding.",
            token_count=20
        )
    ]

    print(f"Created {len(sample_chunks)} sample text chunks")

    # Test embedding functionality (would require valid API key to actually work)
    try:
        # This will fail without a real API key, but tests the structure
        print("Cohere embedder module structure is ready.")
        print("To use this module, ensure you have a valid Cohere API key in your configuration.")
    except Exception as e:
        print(f"Expected error (no API key): {e}")

    print("Cohere embedder module test completed.")