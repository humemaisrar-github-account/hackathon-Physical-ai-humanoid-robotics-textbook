import pytest
from src.services.retrieval_service import RetrievalService
from src.services.performance_validator import PerformanceValidator
from src.lib.test_queries import TEST_QUERIES, TEST_QUERY_CONFIGS
from src.lib.config import Config


class TestQualityValidation:
    """
    Integration tests for quality and performance validation.
    """

    def setup_method(self):
        """
        Set up the retrieval service and performance validator for each test.
        """
        self.service = RetrievalService()
        self.validator = PerformanceValidator(self.service)

    def test_relevance_score_calculation(self):
        """
        Test that relevance scores are calculated properly.
        """
        # Test with a mock result
        from src.models.query import Query
        from src.models.content_chunk import ContentChunk
        from src.models.retrieval_result import RetrievalResult

        mock_query = Query(text="artificial intelligence", top_k=1)
        mock_chunk = ContentChunk(
            id="test_id",
            text="Artificial intelligence is a wonderful field that involves machine learning",
            url="https://example.com",
            section_hierarchy=["Introduction"],
            chunk_id="test_chunk"
        )
        mock_result = RetrievalResult(
            query=mock_query,
            chunks=[mock_chunk],
            scores=[0.8],
            retrieval_time_ms=100.0,
            total_results=1
        )

        relevance_score = self.validator.calculate_relevance_score(mock_result, "artificial intelligence")

        # The score should be between 0 and 1
        assert 0 <= relevance_score <= 1, f"Relevance score {relevance_score} should be between 0 and 1"

    def test_single_test_execution(self):
        """
        Test that a single test can be executed properly.
        """
        test_config = {
            "query": "What is artificial intelligence?",
            "top_k": 2,
            "filters": {},
            "expected_keywords": ["artificial", "intelligence", "AI"]
        }

        result, metrics = self.validator.run_single_test(test_config)

        # Verify metrics structure
        assert "query" in metrics
        assert "relevance_score" in metrics
        assert "response_time_ms" in metrics
        assert "num_results" in metrics
        assert "success" in metrics

        # Verify success flag
        assert metrics["success"] is True, f"Test should succeed, got error: {metrics.get('error', 'None')}"

    def test_full_test_suite(self):
        """
        Test that the full test suite can be executed.
        """
        # Limit to first 3 tests for faster execution in testing
        limited_configs = TEST_QUERY_CONFIGS[:3]

        results = self.validator.run_test_suite(limited_configs)

        # Verify results structure
        assert "total_tests" in results
        assert "successful_tests" in results
        assert "success_rate" in results
        assert "avg_relevance_score" in results
        assert "avg_response_time_ms" in results
        assert "test_results" in results

        # Verify we ran the expected number of tests
        assert results["total_tests"] == len(limited_configs)

    def test_performance_goals_validation(self):
        """
        Test that performance goals are validated correctly.
        """
        # Mock metrics for testing
        mock_metrics = {
            "avg_response_time_ms": 200,  # Under 500ms goal
            "avg_relevance_score": 0.95,  # Above 0.9 goal
            "success_rate": 1.0  # Above 0.9 goal
        }

        validations = self.validator.validate_performance_goals(mock_metrics)

        # All validations should pass with these good metrics
        assert all(validations.values()), f"Not all validations passed: {validations}"

    def test_connection_and_basic_retrieval(self):
        """
        Test that the service can connect and perform basic retrieval.
        """
        connected = self.service.connect_to_qdrant()
        assert connected, "Should be able to connect to Qdrant"

        from src.models.query import Query
        test_query = Query(text="What is AI?", top_k=1)

        result = self.service.retrieve(test_query)

        # Verify result structure
        assert hasattr(result, 'chunks')
        assert hasattr(result, 'scores')
        assert hasattr(result, 'retrieval_time_ms')
        assert hasattr(result, 'total_results')

    @pytest.mark.slow  # Mark as slow to allow skipping in quick test runs
    def test_full_validation_suite(self):
        """
        Test the full validation suite with all test queries.
        This is a comprehensive test that may take longer to run.
        """
        results = self.validator.run_test_suite(TEST_QUERY_CONFIGS)

        # Verify results structure
        assert "total_tests" in results
        assert results["total_tests"] == len(TEST_QUERY_CONFIGS)

        # Validate performance goals
        validations = self.validator.validate_performance_goals(results)

        # Log the results for review
        print(f"Total tests: {results['total_tests']}")
        print(f"Successful tests: {results['successful_tests']}")
        print(f"Success rate: {results['success_rate']:.2%}")
        print(f"Avg relevance score: {results['avg_relevance_score']:.3f}")
        print(f"Avg response time: {results['avg_response_time_ms']:.2f}ms")
        print(f"Performance validations: {validations}")