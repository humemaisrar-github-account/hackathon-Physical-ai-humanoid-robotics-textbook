"""
Common error handling and retry mechanisms for the RAG pipeline.
"""
import time
import random
import functools
from typing import Callable, Type, TypeVar, Optional, Any, Union
from requests import RequestException
from qdrant_client.http.exceptions import UnexpectedResponse
from utils.logging_config import get_logger
from config.config import config

logger = get_logger("error_handling")

T = TypeVar('T')


class PipelineError(Exception):
    """Base exception for pipeline errors."""
    pass


class CrawlError(PipelineError):
    """Exception raised when crawling fails."""
    pass


class ChunkingError(PipelineError):
    """Exception raised when chunking fails."""
    pass


class EmbeddingError(PipelineError):
    """Exception raised when embedding generation fails."""
    pass


class StorageError(PipelineError):
    """Exception raised when storage operations fail."""
    pass


class ValidationError(PipelineError):
    """Exception raised when validation fails."""
    pass


def retry_on_exception(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    logger_instance: Optional[Any] = None
):
    """
    Decorator to retry a function on specific exceptions.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exception types to retry on
        logger_instance: Logger instance to use for logging retries

    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if logger_instance:
                        logger_instance.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {str(e)}"
                        )
                    else:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {str(e)}"
                        )

                    if attempt < max_retries:
                        # Add jitter to avoid thundering herd
                        jitter = random.uniform(0.1, 0.3) * current_delay
                        time.sleep(current_delay + jitter)
                        current_delay *= backoff
                    else:
                        if logger_instance:
                            logger_instance.error(
                                f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}"
                            )
                        else:
                            logger.error(
                                f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}"
                            )

            # If we've exhausted all retries, raise the last exception
            raise last_exception

        return wrapper
    return decorator


def handle_api_errors(
    func: Callable[..., T],
    api_name: str = "API",
    logger_instance: Optional[Any] = None
) -> Callable[..., T]:
    """
    Decorator to handle common API errors with specific logging.

    Args:
        func: Function to wrap
        api_name: Name of the API for logging purposes
        logger_instance: Logger instance to use for logging

    Returns:
        Wrapped function with API error handling
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            if logger_instance:
                logger_instance.info(f"Calling {api_name}")
            else:
                logger.info(f"Calling {api_name}")

            result = func(*args, **kwargs)

            if logger_instance:
                logger_instance.info(f"{api_name} call successful")
            else:
                logger.info(f"{api_name} call successful")

            return result
        except RequestException as e:
            error_msg = f"Request error in {api_name}: {str(e)}"
            if logger_instance:
                logger_instance.error(error_msg)
            else:
                logger.error(error_msg)
            raise CrawlError(error_msg) from e
        except UnexpectedResponse as e:
            error_msg = f"Unexpected response from {api_name}: {str(e)}"
            if logger_instance:
                logger_instance.error(error_msg)
            else:
                logger.error(error_msg)
            raise StorageError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error in {api_name}: {str(e)}"
            if logger_instance:
                logger_instance.error(error_msg)
            else:
                logger.error(error_msg)
            raise PipelineError(error_msg) from e

    return wrapper


def rate_limit_handler(
    func: Callable[..., T],
    rate_limit_delay: float = 1.0,
    logger_instance: Optional[Any] = None
) -> Callable[..., T]:
    """
    Decorator to handle rate limiting by adding delays between calls.

    Args:
        func: Function to wrap
        rate_limit_delay: Delay in seconds between calls
        logger_instance: Logger instance to use for logging

    Returns:
        Wrapped function with rate limiting
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        # Add delay before the call to respect rate limits
        time.sleep(rate_limit_delay)

        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            # Log the error but don't modify the exception
            if logger_instance:
                logger_instance.error(f"Error in rate-limited function {func.__name__}: {str(e)}")
            else:
                logger.error(f"Error in rate-limited function {func.__name__}: {str(e)}")
            raise

    return wrapper


def validate_inputs(
    required_args: Optional[list] = None,
    required_kwargs: Optional[list] = None,
    validator_func: Optional[Callable] = None
):
    """
    Decorator to validate function inputs before execution.

    Args:
        required_args: List of required positional argument names/indices
        required_kwargs: List of required keyword argument names
        validator_func: Custom validation function

    Returns:
        Decorated function with input validation
    """
    if required_args is None:
        required_args = []
    if required_kwargs is None:
        required_kwargs = []

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Validate required positional arguments
            for i, arg_name in enumerate(required_args):
                if isinstance(arg_name, int):  # Index-based validation
                    if i >= len(args):
                        raise ValidationError(f"Required argument at index {i} is missing")
                else:  # Name-based validation (for documentation)
                    if i >= len(args):
                        raise ValidationError(f"Required argument '{arg_name}' is missing")

            # Validate required keyword arguments
            for kwarg_name in required_kwargs:
                if kwarg_name not in kwargs:
                    raise ValidationError(f"Required keyword argument '{kwarg_name}' is missing")

            # Run custom validator if provided
            if validator_func:
                validator_func(*args, **kwargs)

            return func(*args, **kwargs)

        return wrapper
    return decorator


def safe_execute(
    func: Callable[..., T],
    fallback_value: Any = None,
    exceptions: tuple = (Exception,),
    logger_instance: Optional[Any] = None
) -> T:
    """
    Execute a function safely, returning a fallback value if it fails.

    Args:
        func: Function to execute
        fallback_value: Value to return if function fails
        exceptions: Tuple of exceptions to catch
        logger_instance: Logger instance to use for logging

    Returns:
        Result of function execution or fallback value
    """
    try:
        return func()
    except exceptions as e:
        error_msg = f"Function {func.__name__} failed: {str(e)}"
        if logger_instance:
            logger_instance.warning(error_msg)
        else:
            logger.warning(error_msg)
        return fallback_value


def handle_cohere_errors(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator specifically for handling Cohere API errors.

    Args:
        func: Function that calls Cohere API

    Returns:
        Wrapped function with Cohere-specific error handling
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error_str = str(e).lower()

            if "rate limit" in error_str or "429" in error_str:
                raise EmbeddingError(f"Rate limit exceeded when calling Cohere API: {str(e)}") from e
            elif "api key" in error_str or "401" in error_str or "403" in error_str:
                raise EmbeddingError(f"Authentication error with Cohere API: {str(e)}") from e
            elif "500" in error_str or "503" in error_str:
                raise EmbeddingError(f"Server error from Cohere API: {str(e)}") from e
            else:
                raise EmbeddingError(f"Cohere API error: {str(e)}") from e

    return wrapper


def handle_qdrant_errors(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator specifically for handling Qdrant errors.

    Args:
        func: Function that calls Qdrant

    Returns:
        Wrapped function with Qdrant-specific error handling
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            result = func(*args, **kwargs)
            return result
        except UnexpectedResponse as e:
            if e.status_code == 404:
                raise StorageError(f"Qdrant collection not found: {str(e)}") from e
            elif e.status_code == 409:
                raise StorageError(f"Qdrant conflict error (duplicate ID): {str(e)}") from e
            elif e.status_code == 422:
                raise StorageError(f"Qdrant validation error: {str(e)}") from e
            else:
                raise StorageError(f"Qdrant error (status {e.status_code}): {str(e)}") from e
        except Exception as e:
            raise StorageError(f"Qdrant connection error: {str(e)}") from e

    return wrapper


# Common retry configurations for different services
retry_cohere = retry_on_exception(
    max_retries=3,
    delay=config.crawl_delay,
    backoff=2.0,
    exceptions=(EmbeddingError, RequestException),
    logger_instance=logger
)

retry_qdrant = retry_on_exception(
    max_retries=3,
    delay=config.crawl_delay,
    backoff=2.0,
    exceptions=(StorageError, UnexpectedResponse),
    logger_instance=logger
)

retry_crawl = retry_on_exception(
    max_retries=3,
    delay=config.crawl_delay,
    backoff=1.5,
    exceptions=(CrawlError, RequestException),
    logger_instance=logger
)


if __name__ == "__main__":
    # Test the error handling utilities

    # Test retry decorator
    def test_with_counter():
        attempt_count = 0

        @retry_on_exception(max_retries=3, delay=0.1, exceptions=(ValueError,))
        def test_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError(f"Attempt {attempt_count} failed")
            return "Success!"

        try:
            result = test_func()
            print(f"Function result: {result}")
            print(f"Number of attempts: {attempt_count}")
        except Exception as e:
            print(f"Function failed after retries: {e}")

    test_with_counter()

    # Test safe_execute
    def failing_func():
        raise ValueError("This function always fails")

    safe_result = safe_execute(failing_func, fallback_value="Fallback value")
    print(f"Safe execute result: {safe_result}")

    # Test validation decorator
    @validate_inputs(required_kwargs=['name', 'value'])
    def test_validation(name, value, optional=None):
        return f"Name: {name}, Value: {value}, Optional: {optional}"

    try:
        result = test_validation(name="test", value=42)
        print(f"Validation test passed: {result}")
    except ValidationError as e:
        print(f"Validation error: {e}")