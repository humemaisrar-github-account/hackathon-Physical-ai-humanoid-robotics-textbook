"""
Logging module with structured logging for pipeline operations.
"""
import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional
from config.config import config


def setup_logging(
    name: str = "rag_pipeline",
    log_level: int = logging.INFO,
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up structured logging for the pipeline.

    Args:
        name: Name of the logger
        log_level: Logging level (default: INFO)
        log_file: Path to log file (default: pipeline.log in logs directory)
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Prevent adding multiple handlers if logger already exists
    if logger.handlers:
        return logger

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s'
    )

    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(config.logs_dir, f"pipeline_{timestamp}.log")

    # Ensure logs directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "rag_pipeline") -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Name of the logger (default: "rag_pipeline")

    Returns:
        logging.Logger: Logger instance
    """
    return setup_logging(name=name)


def log_pipeline_step(
    logger: logging.Logger,
    step_name: str,
    status: str = "STARTED",
    details: Optional[dict] = None
) -> None:
    """
    Log a pipeline step with structured information.

    Args:
        logger: Logger instance to use
        step_name: Name of the pipeline step
        status: Status of the step (STARTED, COMPLETED, FAILED)
        details: Additional details about the step
    """
    log_msg = f"Pipeline Step: {step_name} - Status: {status}"
    if details:
        log_msg += f" - Details: {details}"

    if status == "FAILED":
        logger.error(log_msg)
    elif status == "COMPLETED":
        logger.info(log_msg)
    else:
        logger.info(log_msg)


def log_progress(
    logger: logging.Logger,
    current: int,
    total: int,
    item_name: str = "items"
) -> None:
    """
    Log progress of a process.

    Args:
        logger: Logger instance to use
        current: Current progress
        total: Total items to process
        item_name: Name of the items being processed
    """
    percentage = (current / total) * 100 if total > 0 else 0
    logger.info(f"Progress: {current}/{total} {item_name} processed ({percentage:.1f}%)")


def log_api_call(
    logger: logging.Logger,
    api_name: str,
    status: str,
    response_time: Optional[float] = None,
    details: Optional[dict] = None
) -> None:
    """
    Log API call with structured information.

    Args:
        logger: Logger instance to use
        api_name: Name of the API being called
        status: Status of the API call
        response_time: Time taken for the API call in seconds
        details: Additional details about the API call
    """
    log_msg = f"API Call: {api_name} - Status: {status}"
    if response_time:
        log_msg += f" - Response Time: {response_time:.3f}s"
    if details:
        log_msg += f" - Details: {details}"

    if status in ["FAILED", "ERROR", "RATE_LIMITED"]:
        logger.error(log_msg)
    else:
        logger.info(log_msg)


# Global logger instance
pipeline_logger = get_logger("rag_pipeline")


if __name__ == "__main__":
    # Test the logging configuration
    logger = get_logger("test_logger")
    logger.info("Testing logger setup")
    log_pipeline_step(logger, "test_step", "STARTED", {"test": True})
    log_progress(logger, 5, 10, "test items")
    log_api_call(logger, "test_api", "SUCCESS", 0.123, {"items": 10})