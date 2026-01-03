import time
from typing import List, Dict, Any, Tuple
from src.models.query import Query
from src.models.retrieval_result import RetrievalResult
from src.services.retrieval_service import RetrievalService
from src.lib.test_queries import TEST_QUERIES, TEST_QUERY_CONFIGS
from src.lib.logger import log_quality_metrics, setup_logger


class PerformanceValidator:
    """
    Service to validate retrieval quality and performance metrics.
    """

    def __init__(self, retrieval_service: RetrievalService):
        """
        Initialize the performance validator with a retrieval service.

        Args:
            retrieval_service: The retrieval service to test
        """
        self.retrieval_service = retrieval_service
        self.logger = setup_logger(__name__)

    def calculate_relevance_score(self, result: RetrievalResult, query_text: str) -> float:
        """
        Calculate a basic relevance score based on content matching.

        Args:
            result: The retrieval result
            query_text: The original query text

        Returns:
            Relevance score between 0 and 1
        """
        if not result.chunks:
            return 0.0

        # Simple relevance calculation based on keyword matching
        query_lower = query_text.lower()
        query_words = set(query_lower.split())

        total_relevance = 0
        for chunk in result.chunks:
            chunk_text = chunk.text.lower()
            chunk_words = set(chunk_text.split())

            # Calculate overlap between query and chunk
            intersection = len(query_words.intersection(chunk_words))
            union = len(query_words.union(chunk_words))

            if union > 0:
                chunk_relevance = intersection / union
                total_relevance += chunk_relevance

        # Average relevance across all chunks
        avg_relevance = total_relevance / len(result.chunks) if result.chunks else 0
        return min(avg_relevance, 1.0)  # Ensure it's between 0 and 1

    def run_single_test(self, query_config: Dict[str, Any]) -> Tuple[RetrievalResult, Dict[str, Any]]:
        """
        Run a single test query and return results with metrics.

        Args:
            query_config: Configuration for the test query

        Returns:
            Tuple of (retrieval result, metrics dict)
        """
        start_time = time.time()

        # Create query object
        query = Query(
            text=query_config["query"],
            top_k=query_config["top_k"],
            filters=query_config["filters"]
        )

        # Perform retrieval
        result = self.retrieval_service.retrieve(query)

        # Calculate metrics
        retrieval_time = result.retrieval_time_ms
        relevance_score = self.calculate_relevance_score(result, query.text)
        response_time = time.time() - start_time

        # Log quality metrics
        log_quality_metrics(
            query=query.text,
            relevance_score=relevance_score,
            response_time=response_time * 1000,  # Convert to milliseconds
            total_results=result.total_results
        )

        metrics = {
            "query": query.text,
            "retrieval_time_ms": retrieval_time,
            "relevance_score": relevance_score,
            "response_time_ms": response_time * 1000,
            "num_results": len(result.chunks),
            "avg_score": sum(result.scores) / len(result.scores) if result.scores else 0,
            "success": True
        }

        return result, metrics

    def run_test_suite(self, test_configs: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the full test suite with predefined queries.

        Args:
            test_configs: List of test configurations (uses default if None)

        Returns:
            Dictionary containing test results and overall metrics
        """
        if test_configs is None:
            test_configs = TEST_QUERY_CONFIGS

        self.logger.info(f"Starting test suite with {len(test_configs)} queries...")

        all_results = []
        all_metrics = []
        successful_tests = 0

        for i, config in enumerate(test_configs):
            try:
                self.logger.info(f"Running test {i+1}/{len(test_configs)}: {config['query'][:50]}...")
                result, metrics = self.run_single_test(config)
                all_results.append(result)
                all_metrics.append(metrics)
                successful_tests += 1
            except Exception as e:
                self.logger.error(f"Test {i+1} failed: {str(e)}")
                # Add failure metrics
                all_metrics.append({
                    "query": config["query"],
                    "retrieval_time_ms": 0,
                    "relevance_score": 0,
                    "response_time_ms": 0,
                    "num_results": 0,
                    "avg_score": 0,
                    "success": False,
                    "error": str(e)
                })

        # Calculate overall metrics
        successful_results = [m for m in all_metrics if m["success"]]
        if successful_results:
            avg_relevance = sum(m["relevance_score"] for m in successful_results) / len(successful_results)
            avg_response_time = sum(m["response_time_ms"] for m in successful_results) / len(successful_results)
            avg_num_results = sum(m["num_results"] for m in successful_results) / len(successful_results)
            avg_scores = sum(m["avg_score"] for m in successful_results) / len(successful_results)
            success_rate = len(successful_results) / len(test_configs)
        else:
            avg_relevance = avg_response_time = avg_num_results = avg_scores = success_rate = 0

        overall_metrics = {
            "total_tests": len(test_configs),
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "avg_relevance_score": avg_relevance,
            "avg_response_time_ms": avg_response_time,
            "avg_num_results": avg_num_results,
            "avg_scores": avg_scores,
            "test_results": all_metrics
        }

        self.logger.info(
            f"Test suite completed. Success rate: {success_rate:.2%}, "
            f"Avg relevance: {avg_relevance:.3f}, Avg time: {avg_response_time:.2f}ms"
        )

        return overall_metrics

    def validate_performance_goals(self, metrics: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate if the performance goals are met.

        Args:
            metrics: Metrics from the test suite

        Returns:
            Dictionary of validation results
        """
        validations = {
            # Performance goal: 95% of queries under 500ms
            "response_time_goal": metrics["avg_response_time_ms"] < 500,
            # Quality goal: 90%+ relevance accuracy
            "relevance_goal": metrics["avg_relevance_score"] >= 0.9,
            # Success rate goal: Most queries should succeed
            "success_rate_goal": metrics["success_rate"] >= 0.9
        }

        # Log validation results
        for goal, passed in validations.items():
            status = "PASSED" if passed else "FAILED"
            self.logger.info(f"Performance validation {goal}: {status}")

        return validations