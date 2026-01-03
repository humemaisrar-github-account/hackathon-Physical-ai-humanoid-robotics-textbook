import pytest
import time
from src.models.query import Query
from src.services.retrieval_service import RetrievalService
from src.lib.config import Config


class TestBasicRetrieval:
    """
    Integration tests for basic retrieval functionality.
    """

    def setup_method(self):
        """
        Set up the retrieval service for each test.
        """
        self.service = RetrievalService()

    def test_connection_to_qdrant(self):
        """
        Test that we can connect to Qdrant.
        """
        # Verify configuration is valid
        assert Config.validate(), "Configuration validation failed"

        # Test connection to Qdrant
        connected = self.service.connect_to_qdrant()
        assert connected, "Failed to connect to Qdrant"

    def test_query_embedding_generation(self):
        """
        Test that query embeddings can be generated successfully.
        """
        test_query = "What is machine learning?"
        embedding = self.service.query_embedding(test_query)

        # Verify embedding is a list of floats
        assert isinstance(embedding, list), "Embedding should be a list"
        assert len(embedding) > 0, "Embedding should not be empty"
        assert all(isinstance(val, (int, float)) for val in embedding), "All embedding values should be numbers"

    def test_retrieval_within_performance_bounds(self):
        """
        Test that retrieval works and meets performance goals (<500ms).
        """
        test_query = Query(
            text="What is RAG?",
            top_k=3
        )

        start_time = time.time()
        result = self.service.retrieve(test_query)
        retrieval_time = result.retrieval_time_ms

        # Verify result structure
        assert hasattr(result, 'chunks'), "Result should have chunks"
        assert hasattr(result, 'scores'), "Result should have scores"
        assert hasattr(result, 'retrieval_time_ms'), "Result should have retrieval time"
        assert hasattr(result, 'total_results'), "Result should have total results"

        # Verify performance goal
        assert retrieval_time < 500, f"Retrieval took {retrieval_time}ms, which exceeds 500ms limit"

        # Verify we got results
        assert isinstance(result.chunks, list), "Chunks should be a list"
        assert len(result.chunks) <= test_query.top_k, f"Should not return more than {test_query.top_k} results"
        assert len(result.scores) == len(result.chunks), "Scores and chunks should have same length"

        # Verify scores are in valid range
        for score in result.scores:
            assert 0 <= score <= 1, f"Score {score} should be between 0 and 1"

    def test_retrieval_with_filters(self):
        """
        Test that retrieval works with filters.
        """
        test_query = Query(
            text="What is artificial intelligence?",
            top_k=2,
            filters={"url": "https://example.com/test"}  # This filter might not match anything but should not error
        )

        result = self.service.retrieve(test_query)

        # Verify result structure
        assert hasattr(result, 'chunks'), "Result should have chunks"
        assert hasattr(result, 'scores'), "Result should have scores"

    def test_retrieval_with_empty_query(self):
        """
        Test that empty queries are handled properly.
        """
        with pytest.raises(Exception):
            empty_query = Query(text="", top_k=3)
            self.service.retrieve(empty_query)

    def test_retrieval_with_large_top_k(self):
        """
        Test that large top_k values are handled properly.
        """
        test_query = Query(
            text="What is AI?",
            top_k=10  # Within valid range
        )

        result = self.service.retrieve(test_query)

        assert len(result.chunks) <= test_query.top_k, "Should not return more results than top_k"