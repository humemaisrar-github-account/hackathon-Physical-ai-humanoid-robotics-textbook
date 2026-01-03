import logging
import time
from typing import Dict, Any, Optional


def setup_logger(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with the specified name and level.

    Args:
        name: Name of the logger
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding multiple handlers if logger already exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def log_performance(
    operation: str,
    start_time: float,
    additional_info: Optional[Dict[str, Any]] = None
) -> float:
    """
    Log performance metrics for an operation.

    Args:
        operation: Name of the operation being measured
        start_time: Start time of the operation (from time.time())
        additional_info: Additional information to log

    Returns:
        Elapsed time in milliseconds
    """
    end_time = time.time()
    elapsed_ms = (end_time - start_time) * 1000

    logger = setup_logger("performance")
    log_msg = f"{operation} completed in {elapsed_ms:.2f}ms"

    if additional_info:
        info_str = ", ".join([f"{k}={v}" for k, v in additional_info.items()])
        log_msg += f" | {info_str}"

    logger.info(log_msg)
    return elapsed_ms


def log_retrieval_metrics(
    query: str,
    num_results: int,
    retrieval_time_ms: float,
    avg_score: Optional[float] = None,
    scores: Optional[list] = None
) -> None:
    """
    Log specific metrics for retrieval operations.

    Args:
        query: The query text
        num_results: Number of results returned
        retrieval_time_ms: Time taken for retrieval in milliseconds
        avg_score: Average similarity score of results
        scores: List of all similarity scores
    """
    logger = setup_logger("retrieval")
    log_msg = (
        f"Retrieval query: '{query[:50]}...', "
        f"results: {num_results}, "
        f"time: {retrieval_time_ms:.2f}ms"
    )

    if avg_score is not None:
        log_msg += f", avg_score: {avg_score:.3f}"

    if scores is not None:
        min_score = min(scores) if scores else 0
        max_score = max(scores) if scores else 0
        log_msg += f", min_score: {min_score:.3f}, max_score: {max_score:.3f}"

    logger.info(log_msg)


def log_quality_metrics(
    query: str,
    relevance_score: float,
    response_time: float,
    total_results: int
) -> None:
    """
    Log quality metrics for retrieval validation.

    Args:
        query: The query text
        relevance_score: Relevance score of the results
        response_time: Time taken for retrieval
        total_results: Total number of results returned
    """
    logger = setup_logger("quality")
    log_msg = (
        f"Quality validation for query: '{query[:50]}...', "
        f"relevance: {relevance_score:.3f}, "
        f"time: {response_time:.2f}ms, "
        f"results: {total_results}"
    )
    logger.info(log_msg)


def log_error(error: Exception, context: str = "") -> None:
    """
    Log error with context information.

    Args:
        error: The exception that occurred
        context: Context information about where the error occurred
    """
    logger = setup_logger("error")
    error_msg = f"Error in {context}: {str(error)}" if context else f"Error: {str(error)}"
    logger.error(error_msg, exc_info=True)