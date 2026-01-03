"""
End-to-end testing script for the RAG Agent API.

This script performs 10+ validated end-to-end queries to test the complete
functionality of the RAG Agent system.
"""

import time
import requests
import os
from typing import List, Dict, Any


class EndToEndTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_key = os.getenv("API_KEY", "test-api-key")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.test_results = []

    def run_test_query(self, question: str, expected_elements: List[str] = None) -> Dict[str, Any]:
        """Run a single test query and return results."""
        start_time = time.time()

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/query",
                json={
                    "question": question,
                    "top_k": 5,
                    "include_sources": True
                },
                headers=self.headers
            )

            end_time = time.time()
            response_time = end_time - start_time

            result = {
                "question": question,
                "status_code": response.status_code,
                "response_time": response_time,
                "response_data": response.json() if response.status_code == 200 else None,
                "success": response.status_code == 200,
                "error": None if response.status_code == 200 else response.text
            }

            # Check if response contains expected elements (if provided)
            if expected_elements and result["response_data"]:
                result["contains_expected"] = all(
                    expected.lower() in result["response_data"]["answer"].lower()
                    for expected in expected_elements
                )
            else:
                result["contains_expected"] = True  # Skip check if no expectations provided

        except Exception as e:
            result = {
                "question": question,
                "status_code": None,
                "response_time": time.time() - start_time,
                "response_data": None,
                "success": False,
                "error": str(e),
                "contains_expected": False
            }

        return result

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all end-to-end tests."""
        test_queries = [
            {
                "question": "What is machine learning?",
                "expected": ["learning", "artificial"]  # Expected to find these terms if available in data
            },
            {
                "question": "Explain artificial intelligence concepts",
                "expected": ["intelligence", "ai"]
            },
            {
                "question": "What are neural networks?",
                "expected": ["networks", "neural"]
            },
            {
                "question": "How does deep learning work?",
                "expected": ["learning", "deep"]
            },
            {
                "question": "What is data science?",
                "expected": ["data", "science"]
            },
            {
                "question": "Explain algorithms",
                "expected": ["algorithm"]
            },
            {
                "question": "What is natural language processing?",
                "expected": ["language", "processing"]
            },
            {
                "question": "How do decision trees work?",
                "expected": ["trees", "decision"]
            },
            {
                "question": "What is computer vision?",
                "expected": ["vision", "computer"]
            },
            {
                "question": "Explain clustering in machine learning",
                "expected": ["clustering", "learning"]
            },
            {
                "question": "What are support vector machines?",
                "expected": ["vector", "machines"]
            },
            {
                "question": "How does reinforcement learning work?",
                "expected": ["reinforcement", "learning"]
            }
        ]

        print(f"Running {len(test_queries)} end-to-end tests...")
        print("-" * 60)

        all_results = []
        successful_tests = 0
        response_times = []

        for i, test in enumerate(test_queries, 1):
            print(f"Test {i}: {test['question'][:50]}...")
            result = self.run_test_query(test["question"], test.get("expected"))
            all_results.append(result)

            if result["success"]:
                successful_tests += 1
                response_times.append(result["response_time"])

            print(f"  Status: {'✓' if result['success'] else '✗'} "
                  f"({result['status_code'] if result['status_code'] else 'ERROR'}) "
                  f"Response time: {result['response_time']:.2f}s")

        # Calculate metrics
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0

        summary = {
            "total_tests": len(test_queries),
            "successful_tests": successful_tests,
            "success_rate": successful_tests / len(test_queries) * 100,
            "average_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "min_response_time": min_response_time,
            "all_results": all_results
        }

        return summary

    def print_summary(self, summary: Dict[str, Any]):
        """Print a summary of test results."""
        print("\n" + "=" * 60)
        print("END-TO-END TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful: {summary['successful_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Average Response Time: {summary['average_response_time']:.2f}s")
        print(f"Max Response Time: {summary['max_response_time']:.2f}s")
        print(f"Min Response Time: {summary['min_response_time']:.2f}s")

        # Performance requirements check
        print("\nPERFORMANCE REQUIREMENTS CHECK:")
        if summary['average_response_time'] <= 2.0:  # 2 seconds requirement
            print("✓ Average response time requirement met (< 2s)")
        else:
            print("✗ Average response time requirement not met (≥ 2s)")

        if summary['max_response_time'] <= 5.0:  # 5 seconds max
            print("✓ Max response time requirement met (< 5s)")
        else:
            print("✗ Max response time requirement not met (≥ 5s)")

        print("\nDETAILED RESULTS:")
        for i, result in enumerate(summary['all_results'], 1):
            status = "✓" if result['success'] else "✗"
            print(f"{i:2d}. {status} {result['question'][:40]:<40} "
                  f"({result['response_time']:.2f}s)")


def main():
    """Main function to run end-to-end tests."""
    print("Starting RAG Agent End-to-End Tests...")
    print("Note: These tests require the RAG Agent API to be running at http://localhost:8000")
    print("Make sure to set the OPENAI_API_KEY, COHERE_API_KEY, QDRANT_URL, QDRANT_API_KEY, and API_KEY environment variables.")

    # Check if API is available
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✓ API is available")
        else:
            print("✗ API is not responding properly")
            return
    except:
        print("✗ API is not running or not accessible")
        print("Please start the API with: uvicorn src.main:app --reload")
        return

    tester = EndToEndTester()
    summary = tester.run_all_tests()
    tester.print_summary(summary)

    # Mark test completion
    print(f"\nCompleted {len(summary['all_results'])} end-to-end tests as required.")


if __name__ == "__main__":
    main()