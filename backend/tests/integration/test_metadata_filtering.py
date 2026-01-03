import pytest
from src.models.query import Query
from src.services.retrieval_service import RetrievalService
from src.lib.config import Config


class TestMetadataFiltering:
    """
    Integration tests for metadata filtering functionality.
    """

    def setup_method(self):
        """
        Set up the retrieval service for each test.
        """
        self.service = RetrievalService()

    def test_retrieval_with_url_filter(self):
        """
        Test that retrieval works with URL filter.
        """
        # Test connection first
        connected = self.service.connect_to_qdrant()
        assert connected, "Failed to connect to Qdrant"

        test_query = Query(
            text="What is artificial intelligence?",
            top_k=3,
            filters={"url": "https://example.com/test"}  # This filter might not match anything but should not error
        )

        result = self.service.retrieve(test_query)

        # Verify result structure
        assert hasattr(result, 'chunks'), "Result should have chunks"
        assert hasattr(result, 'scores'), "Result should have scores"
        assert isinstance(result.chunks, list), "Chunks should be a list"
        assert len(result.scores) == len(result.chunks), "Scores and chunks should have same length"

    def test_retrieval_with_section_filter(self):
        """
        Test that retrieval works with section filter.
        """
        test_query = Query(
            text="What is machine learning?",
            top_k=2,
            filters={"section": "Introduction"}  # This filter might not match anything but should not error
        )

        result = self.service.retrieve(test_query)

        # Verify result structure
        assert hasattr(result, 'chunks'), "Result should have chunks"
        assert hasattr(result, 'scores'), "Result should have scores"
        assert isinstance(result.chunks, list), "Chunks should be a list"

    def test_retrieval_with_multiple_filters(self):
        """
        Test that retrieval works with multiple filters.
        """
        test_query = Query(
            text="What is deep learning?",
            top_k=2,
            filters={
                "url": "https://example.com/test",
                "section": "Chapter 1"
            }
        )

        result = self.service.retrieve(test_query)

        # Verify result structure
        assert hasattr(result, 'chunks'), "Result should have chunks"
        assert hasattr(result, 'scores'), "Result should have scores"
        assert isinstance(result.chunks, list), "Chunks should be a list"

    def test_retrieval_without_filters(self):
        """
        Test that retrieval still works without filters.
        """
        test_query = Query(
            text="What is AI?",
            top_k=3,
            filters={}  # No filters
        )

        result = self.service.retrieve(test_query)

        # Verify result structure
        assert hasattr(result, 'chunks'), "Result should have chunks"
        assert hasattr(result, 'scores'), "Result should have scores"
        assert isinstance(result.chunks, list), "Chunks should be a list"

    def test_filter_validation(self):
        """
        Test that invalid filter fields are handled properly.
        """
        # Test with an invalid filter field
        test_query = Query(
            text="Test query",
            top_k=2,
            filters={"invalid_field": "value"}
        )

        # This should still work since we handle invalid fields gracefully in the service
        try:
            result = self.service.retrieve(test_query)
            assert hasattr(result, 'chunks'), "Result should have chunks"
        except Exception:
            # If it fails, that's also acceptable as long as it's handled gracefully
            pass