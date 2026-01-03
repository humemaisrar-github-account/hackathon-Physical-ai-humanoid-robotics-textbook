import argparse
import json
import sys
from typing import Dict, Any
from src.models.query import Query
from src.services.retrieval_service import RetrievalService
from src.services.performance_validator import PerformanceValidator
from src.lib.test_queries import TEST_QUERIES
from src.lib.logger import setup_logger


class RetrievalCLI:
    """
    Command-line interface for the retrieval pipeline.
    """

    def __init__(self):
        """
        Initialize the CLI with a retrieval service instance.
        """
        self.service = RetrievalService()
        self.logger = setup_logger(__name__)

    def create_parser(self) -> argparse.ArgumentParser:
        """
        Create and configure the argument parser.

        Returns:
            Configured ArgumentParser instance
        """
        parser = argparse.ArgumentParser(
            description="Semantic retrieval pipeline for querying book content"
        )

        # Main query argument
        parser.add_argument(
            "--query",
            type=str,
            required=False,  # Made optional since --run-tests doesn't need it
            help="The natural language query text"
        )

        # Top-K argument
        parser.add_argument(
            "--top-k",
            type=int,
            default=3,
            help="Number of results to return (default: 3)"
        )

        # Filter arguments
        parser.add_argument(
            "--filter-url",
            type=str,
            help="Filter results by source URL"
        )

        parser.add_argument(
            "--filter-section",
            type=str,
            help="Filter results by section"
        )

        # Test mode
        parser.add_argument(
            "--run-tests",
            action="store_true",
            help="Execute the test suite with predefined queries"
        )

        return parser

    def process_query(self, args) -> Dict[str, Any]:
        """
        Process a query from command line arguments.

        Args:
            args: Parsed command line arguments

        Returns:
            Dictionary containing the retrieval result
        """
        # Build filters from arguments
        filters = {}
        if args.filter_url:
            filters["url"] = args.filter_url
        if args.filter_section:
            filters["section"] = args.filter_section

        # Create query object
        query = Query(
            text=args.query,
            top_k=args.top_k,
            filters=filters
        )

        # Perform retrieval
        result = self.service.retrieve(query)

        # Convert to dictionary for JSON output
        result_dict = {
            "query": result.query.text,
            "chunks": [chunk.dict() for chunk in result.chunks],
            "scores": result.scores,
            "retrieval_time_ms": result.retrieval_time_ms,
            "total_results": result.total_results
        }

        return result_dict

    def run(self, args=None) -> int:
        """
        Run the CLI with the provided arguments.

        Args:
            args: Command line arguments (if None, will parse from sys.argv)

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        try:
            parser = self.create_parser()
            args = parser.parse_args(args)

            # Check if we should run tests
            if args.run_tests:
                self.logger.info("Running comprehensive test suite...")

                # Create a performance validator
                validator = PerformanceValidator(self.service)

                # Run the full test suite
                results = validator.run_test_suite()

                # Validate performance goals
                validations = validator.validate_performance_goals(results)

                # Combine results for output
                output = {
                    "test_results": results,
                    "validations": validations,
                    "summary": {
                        "total_tests": results["total_tests"],
                        "successful_tests": results["successful_tests"],
                        "success_rate": results["success_rate"],
                        "avg_relevance_score": results["avg_relevance_score"],
                        "avg_response_time_ms": results["avg_response_time_ms"],
                        "all_goals_met": all(validations.values())
                    }
                }

                print(json.dumps(output, indent=2))
                return 0

            # Process the query
            result = self.process_query(args)

            # Output the result in JSON format
            print(json.dumps(result, indent=2))

            return 0

        except KeyboardInterrupt:
            self.logger.info("Operation cancelled by user")
            return 130  # Standard exit code for Ctrl+C
        except Exception as e:
            self.logger.error(f"Error in CLI: {str(e)}")
            print(f"Error: {str(e)}", file=sys.stderr)
            return 1


def main():
    """
    Main entry point for the CLI.
    """
    cli = RetrievalCLI()
    exit_code = cli.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()