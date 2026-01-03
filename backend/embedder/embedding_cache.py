"""
Embedding caching module to avoid regeneration.
"""
import hashlib
import json
import os
from typing import List, Optional, Dict, Any
from pathlib import Path

from utils.logging_config import get_logger
from config.config import config

logger = get_logger("embedding_cache")


class EmbeddingCache:
    """
    Cache for storing and retrieving embeddings to avoid regeneration.
    """
    def __init__(self, cache_dir: str = None):
        """
        Initialize the embedding cache.

        Args:
            cache_dir: Directory to store cache files (defaults to embeddings dir in config)
        """
        self.cache_dir = Path(cache_dir or config.embeddings_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "embedding_cache.json"
        self.cache_data = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        """
        Load cache data from file.

        Returns:
            Dict containing cached embeddings
        """
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load cache file {self.cache_file}: {e}")
                return {}
        return {}

    def _save_cache(self) -> None:
        """
        Save cache data to file.
        """
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, indent=2)
        except IOError as e:
            logger.error(f"Could not save cache file {self.cache_file}: {e}")

    def _generate_key(self, text: str, model_name: str) -> str:
        """
        Generate a unique key for caching based on text and model.

        Args:
            text: Text to generate key for
            model_name: Model name to include in key

        Returns:
            str: Unique cache key
        """
        content = f"{text}:{model_name}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

    def get_embedding(self, text: str, model_name: str = "default") -> Optional[List[float]]:
        """
        Get embedding from cache if available.

        Args:
            text: Text to get embedding for
            model_name: Model name to use for cache key

        Returns:
            Cached embedding vector or None if not in cache
        """
        key = self._generate_key(text, model_name)
        embedding = self.cache_data.get(key)

        if embedding is not None:
            logger.debug(f"Cache hit for key: {key}")
            return embedding

        logger.debug(f"Cache miss for key: {key}")
        return None

    def set_embedding(self, text: str, embedding: List[float], model_name: str = "default") -> None:
        """
        Store embedding in cache.

        Args:
            text: Text that was embedded
            embedding: Embedding vector to cache
            model_name: Model name used for embedding
        """
        key = self._generate_key(text, model_name)
        self.cache_data[key] = embedding
        self._save_cache()
        logger.debug(f"Stored embedding in cache with key: {key}")

    def is_cached(self, text: str, model_name: str = "default") -> bool:
        """
        Check if embedding is already in cache.

        Args:
            text: Text to check
            model_name: Model name to use for cache key

        Returns:
            bool: True if embedding is in cache, False otherwise
        """
        key = self._generate_key(text, model_name)
        return key in self.cache_data

    def clear_cache(self) -> None:
        """
        Clear all cached embeddings.
        """
        self.cache_data = {}
        self._save_cache()
        logger.info("Cleared embedding cache")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.

        Returns:
            Dict containing cache statistics
        """
        return {
            "cache_size": len(self.cache_data),
            "cache_file": str(self.cache_file),
            "cache_dir": str(self.cache_dir)
        }


def create_embedding_cache(cache_dir: str = None) -> EmbeddingCache:
    """
    Create an embedding cache instance.

    Args:
        cache_dir: Directory to store cache files (defaults to config value)

    Returns:
        EmbeddingCache: Configured embedding cache instance
    """
    return EmbeddingCache(cache_dir)


def get_cached_embedding(text: str, model_name: str = "default", cache_dir: str = None) -> Optional[List[float]]:
    """
    Get embedding from cache if available.

    Args:
        text: Text to get embedding for
        model_name: Model name to use for cache key
        cache_dir: Directory to store cache files (defaults to config value)

    Returns:
        Cached embedding vector or None if not in cache
    """
    cache = EmbeddingCache(cache_dir)
    return cache.get_embedding(text, model_name)


def cache_embedding(text: str, embedding: List[float], model_name: str = "default", cache_dir: str = None) -> None:
    """
    Store embedding in cache.

    Args:
        text: Text that was embedded
        embedding: Embedding vector to cache
        model_name: Model name used for embedding
        cache_dir: Directory to store cache files (defaults to config value)
    """
    cache = EmbeddingCache(cache_dir)
    cache.set_embedding(text, embedding, model_name)


def is_embedding_cached(text: str, model_name: str = "default", cache_dir: str = None) -> bool:
    """
    Check if embedding is already in cache.

    Args:
        text: Text to check
        model_name: Model name to use for cache key
        cache_dir: Directory to store cache files (defaults to config value)

    Returns:
        bool: True if embedding is in cache, False otherwise
    """
    cache = EmbeddingCache(cache_dir)
    return cache.is_cached(text, model_name)


# Global cache instance
_global_cache = None


def get_global_embedding_cache() -> EmbeddingCache:
    """
    Get the global embedding cache instance.

    Returns:
        EmbeddingCache: Global cache instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = EmbeddingCache()
    return _global_cache


if __name__ == "__main__":
    # Test the embedding cache
    print("Testing embedding cache...")

    # Create a cache instance
    cache = EmbeddingCache()

    # Test storing and retrieving an embedding
    test_text = "This is a test sentence for caching."
    test_embedding = [0.1, 0.2, 0.3, 0.4, 0.5] * 100  # Simulate a real embedding

    # Check if it's cached (should be False)
    is_cached = cache.is_cached(test_text)
    print(f"Is '{test_text}' cached? {is_cached}")

    # Store the embedding
    cache.set_embedding(test_text, test_embedding)
    print(f"Stored embedding for: '{test_text[:20]}...'")

    # Check if it's cached now (should be True)
    is_cached = cache.is_cached(test_text)
    print(f"Is '{test_text}' cached after storing? {is_cached}")

    # Retrieve the embedding
    retrieved_embedding = cache.get_embedding(test_text)
    print(f"Retrieved embedding length: {len(retrieved_embedding) if retrieved_embedding else 0}")

    # Compare embeddings
    embeddings_match = retrieved_embedding == test_embedding
    print(f"Do embeddings match? {embeddings_match}")

    # Get cache stats
    stats = cache.get_cache_stats()
    print(f"Cache stats: {stats}")

    print("Embedding cache test completed!")