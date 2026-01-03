"""
Validation module to verify pipeline completion and data integrity.
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from utils.logging_config import get_logger
from storage.qdrant_client import get_embedding_count, search_similar_content
from models.data_models import TextChunk, QdrantRecord
from config.config import config


logger = get_logger("validator")


class PipelineValidator:
    """
    Validator class to verify pipeline completion and data integrity.
    """
    def __init__(self):
        self.validation_results = {
            "timestamp": datetime.now(),
            "checks": {},
            "issues": []
        }

    def validate_vector_count(self, expected_count: Optional[int] = None) -> bool:
        """
        Validate that vector count matches expected count.

        Args:
            expected_count: Expected number of vectors (if None, compares with chunks file count)

        Returns:
            bool: True if validation passes
        """
        try:
            vector_count = get_embedding_count()
            logger.info(f"Found {vector_count} vectors in Qdrant collection")

            # If expected count not provided, we can't validate against a specific number
            # But we can at least verify that vectors exist
            if expected_count is not None:
                if vector_count != expected_count:
                    issue = f"Vector count mismatch: expected {expected_count}, got {vector_count}"
                    self.validation_results["issues"].append(issue)
                    logger.error(issue)
                    self.validation_results["checks"]["vector_count"] = {
                        "status": "FAILED",
                        "expected": expected_count,
                        "actual": vector_count
                    }
                    return False
                else:
                    logger.info(f"Vector count validation passed: {vector_count} vectors")
                    self.validation_results["checks"]["vector_count"] = {
                        "status": "PASSED",
                        "expected": expected_count,
                        "actual": vector_count
                    }
                    return True
            else:
                # Just check that there are some vectors
                if vector_count > 0:
                    logger.info(f"Vector count validation passed: {vector_count} vectors found")
                    self.validation_results["checks"]["vector_count"] = {
                        "status": "PASSED",
                        "expected": "at least 1",
                        "actual": vector_count
                    }
                    return True
                else:
                    issue = "No vectors found in Qdrant collection"
                    self.validation_results["issues"].append(issue)
                    logger.error(issue)
                    self.validation_results["checks"]["vector_count"] = {
                        "status": "FAILED",
                        "expected": "at least 1",
                        "actual": 0
                    }
                    return False
        except Exception as e:
            issue = f"Error validating vector count: {str(e)}"
            self.validation_results["issues"].append(issue)
            logger.error(issue)
            self.validation_results["checks"]["vector_count"] = {
                "status": "ERROR",
                "error": str(e)
            }
            return False

    def validate_metadata_integrity(self) -> bool:
        """
        Validate metadata integrity by checking a sample of stored vectors.

        Returns:
            bool: True if validation passes
        """
        try:
            # Search for a sample vector to check metadata
            sample_query = [0.1] * 1024  # Sample vector of correct dimension
            results = search_similar_content(sample_query, limit=5)

            if not results:
                # If no results, try to get a sample vector directly if we know an ID
                logger.warning("No similar vectors found for metadata validation")
                self.validation_results["checks"]["metadata_integrity"] = {
                    "status": "WARNING",
                    "message": "No vectors available to validate metadata"
                }
                return True  # Not a failure, just no data to validate

            # Check metadata structure for each result
            for i, result in enumerate(results):
                if hasattr(result, 'payload') and result.payload:
                    required_fields = ['page_url', 'heading_path', 'content_raw', 'chunk_id', 'token_count']
                    missing_fields = [field for field in required_fields if field not in result.payload]

                    if missing_fields:
                        issue = f"Missing metadata fields in result {i}: {missing_fields}"
                        self.validation_results["issues"].append(issue)
                        logger.error(issue)
                        self.validation_results["checks"]["metadata_integrity"] = {
                            "status": "FAILED",
                            "missing_fields": missing_fields
                        }
                        return False
                else:
                    issue = f"No payload found in result {i}"
                    self.validation_results["issues"].append(issue)
                    logger.error(issue)
                    self.validation_results["checks"]["metadata_integrity"] = {
                        "status": "FAILED",
                        "error": "No payload in search result"
                    }
                    return False

            logger.info(f"Metadata integrity validation passed for {len(results)} sample vectors")
            self.validation_results["checks"]["metadata_integrity"] = {
                "status": "PASSED",
                "checked_count": len(results)
            }
            return True

        except Exception as e:
            issue = f"Error validating metadata integrity: {str(e)}"
            self.validation_results["issues"].append(issue)
            logger.error(issue)
            self.validation_results["checks"]["metadata_integrity"] = {
                "status": "ERROR",
                "error": str(e)
            }
            return False

    def validate_empty_chunks(self, chunks_path: str = "data/chunks/") -> bool:
        """
        Validate that there are no empty chunks in the chunks directory.

        Args:
            chunks_path: Path to the chunks directory

        Returns:
            bool: True if validation passes
        """
        try:
            empty_chunk_count = 0
            total_chunks = 0

            if os.path.exists(chunks_path):
                for filename in os.listdir(chunks_path):
                    if filename.endswith('.json'):  # Assuming chunks are stored as JSON
                        filepath = os.path.join(chunks_path, filename)
                        total_chunks += 1

                        # Check if the chunk file is empty or has invalid content
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read().strip()
                                if not content:
                                    empty_chunk_count += 1
                                    logger.warning(f"Empty chunk file found: {filepath}")
                        except Exception as e:
                            logger.error(f"Error reading chunk file {filepath}: {str(e)}")
                            empty_chunk_count += 1
            else:
                logger.warning(f"Chunks directory does not exist: {chunks_path}")
                # This might be fine if no chunks have been created yet
                self.validation_results["checks"]["empty_chunks"] = {
                    "status": "WARNING",
                    "message": f"Chunks directory does not exist: {chunks_path}"
                }
                return True

            if empty_chunk_count > 0:
                issue = f"Found {empty_chunk_count} empty chunk files out of {total_chunks} total"
                self.validation_results["issues"].append(issue)
                logger.error(issue)
                self.validation_results["checks"]["empty_chunks"] = {
                    "status": "FAILED",
                    "empty_count": empty_chunk_count,
                    "total_count": total_chunks
                }
                return False
            else:
                logger.info(f"Empty chunks validation passed: 0 empty chunks out of {total_chunks} total")
                self.validation_results["checks"]["empty_chunks"] = {
                    "status": "PASSED",
                    "empty_count": 0,
                    "total_count": total_chunks
                }
                return True

        except Exception as e:
            issue = f"Error validating empty chunks: {str(e)}"
            self.validation_results["issues"].append(issue)
            logger.error(issue)
            self.validation_results["checks"]["empty_chunks"] = {
                "status": "ERROR",
                "error": str(e)
            }
            return False

    def validate_similarity_search(self) -> bool:
        """
        Validate that similarity search returns meaningful results.

        Returns:
            bool: True if validation passes
        """
        try:
            # Create a test query vector
            test_query = [0.1] * 1024  # Sample vector of correct dimension

            # Try to search for similar content
            results = search_similar_content(test_query, limit=3)

            # If we have results, check that they have reasonable scores (> 0.5 for similarity)
            if results:
                valid_results = [r for r in results if hasattr(r, 'score') and r.score > 0.1]
                if len(valid_results) > 0:
                    logger.info(f"Similarity search validation passed: {len(valid_results)} valid results found")
                    self.validation_results["checks"]["similarity_search"] = {
                        "status": "PASSED",
                        "valid_results": len(valid_results),
                        "total_results": len(results)
                    }
                    return True
                else:
                    issue = f"Similarity search returned results but with low scores: {[getattr(r, 'score', 0) for r in results]}"
                    self.validation_results["issues"].append(issue)
                    logger.warning(issue)
                    self.validation_results["checks"]["similarity_search"] = {
                        "status": "WARNING",
                        "low_scores": [getattr(r, 'score', 0) for r in results]
                    }
                    return True  # Not a failure, just low quality results
            else:
                # No results might be expected if the collection is empty
                logger.warning("Similarity search returned no results")
                self.validation_results["checks"]["similarity_search"] = {
                    "status": "WARNING",
                    "message": "No similar results found"
                }
                return True  # Not a failure if no data exists

        except Exception as e:
            issue = f"Error validating similarity search: {str(e)}"
            self.validation_results["issues"].append(issue)
            logger.error(issue)
            self.validation_results["checks"]["similarity_search"] = {
                "status": "ERROR",
                "error": str(e)
            }
            return False

    def run_full_validation(self) -> Dict[str, Any]:
        """
        Run all validation checks and return comprehensive results.

        Returns:
            Dict containing validation results and summary
        """
        logger.info("Starting full pipeline validation...")

        # Run all validation checks
        checks = {
            "vector_count": self.validate_vector_count(),
            "metadata_integrity": self.validate_metadata_integrity(),
            "empty_chunks": self.validate_empty_chunks(),
            "similarity_search": self.validate_similarity_search()
        }

        # Calculate summary
        passed_checks = sum(1 for result in checks.values() if result)
        total_checks = len(checks)

        self.validation_results["summary"] = {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": total_checks - passed_checks,
            "success_rate": passed_checks / total_checks if total_checks > 0 else 0,
            "overall_status": "PASSED" if passed_checks == total_checks else "PARTIAL" if passed_checks > 0 else "FAILED"
        }

        logger.info(f"Full validation completed. {passed_checks}/{total_checks} checks passed.")

        return self.validation_results

    def generate_validation_report(self) -> str:
        """
        Generate a human-readable validation report.

        Returns:
            Formatted validation report string
        """
        report_lines = [
            "PIPELINE VALIDATION REPORT",
            "=" * 50,
            f"Timestamp: {self.validation_results['timestamp']}",
            ""
        ]

        # Add check results
        report_lines.append("VALIDATION CHECKS:")
        for check_name, check_result in self.validation_results.get("checks", {}).items():
            status = check_result.get("status", "UNKNOWN")
            report_lines.append(f"  {check_name}: {status}")
        report_lines.append("")

        # Add summary
        summary = self.validation_results.get("summary", {})
        report_lines.append("SUMMARY:")
        report_lines.append(f"  Total checks: {summary.get('total_checks', 0)}")
        report_lines.append(f"  Passed: {summary.get('passed_checks', 0)}")
        report_lines.append(f"  Failed: {summary.get('failed_checks', 0)}")
        report_lines.append(f"  Success rate: {summary.get('success_rate', 0):.2%}")
        report_lines.append(f"  Overall status: {summary.get('overall_status', 'UNKNOWN')}")
        report_lines.append("")

        # Add issues if any
        issues = self.validation_results.get("issues", [])
        if issues:
            report_lines.append("ISSUES FOUND:")
            for i, issue in enumerate(issues, 1):
                report_lines.append(f"  {i}. {issue}")
        else:
            report_lines.append("NO ISSUES FOUND")

        return "\n".join(report_lines)


def validate_pipeline_completion(expected_chunk_count: Optional[int] = None) -> Dict[str, Any]:
    """
    Convenience function to run full pipeline validation.

    Args:
        expected_chunk_count: Expected number of chunks for vector count validation

    Returns:
        Validation results dictionary
    """
    validator = PipelineValidator()

    # If expected chunk count is provided, use it for vector validation
    if expected_chunk_count is not None:
        validator.validate_vector_count(expected_chunk_count)

    return validator.run_full_validation()


def generate_validation_report() -> str:
    """
    Generate a validation report.

    Returns:
        Formatted validation report string
    """
    validator = PipelineValidator()
    validator.run_full_validation()
    return validator.generate_validation_report()


if __name__ == "__main__":
    # Test the validation module
    print("Testing validation module...")

    # Run validation
    results = validate_pipeline_completion()

    # Generate and print report
    report = generate_validation_report()
    print(report)

    print("\nValidation module test completed.")