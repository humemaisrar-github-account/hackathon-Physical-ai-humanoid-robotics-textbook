"""
Request/Response logging middleware and authentication for the RAG Agent API.

This module provides middleware for logging requests/responses and authenticating API calls.
"""

import time
import logging
from typing import Callable, Awaitable
from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from src.config.settings import settings


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_api_key(request: Request) -> str:
    """
    Extract the API key from the request headers.

    Args:
        request: The incoming request

    Returns:
        The API key from the Authorization header
    """
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Authorization header"
        )

    api_key = authorization[7:]  # Remove "Bearer " prefix
    return api_key


def verify_api_key(api_key: str) -> bool:
    """
    Verify the provided API key against the expected value.

    In a production system, this would check against a database or other secure storage.
    For now, we'll check against a fixed value or environment variable.

    Args:
        api_key: The API key to verify

    Returns:
        True if the key is valid, False otherwise
    """
    # For this implementation, we'll use a simple check
    # In a real application, you'd want to validate against a secure store
    expected_api_key = getattr(settings, 'api_key', None)

    # If no expected API key is set in settings, authentication is disabled
    if not expected_api_key:
        return True

    return api_key == expected_api_key


async def logging_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """
    Middleware to log incoming requests and outgoing responses.

    Args:
        request: The incoming request
        call_next: The next middleware/function in the chain

    Returns:
        The response from the next middleware/function
    """
    start_time = time.time()

    # Log request
    logger.info(f"Request: {request.method} {request.url.path} - Client: {request.client.host}")
    if request.query_params:
        logger.debug(f"Query params: {dict(request.query_params)}")

    try:
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Add processing time to response headers
        response.headers["X-Process-Time"] = str(process_time)

        # Log response
        logger.info(f"Response: {response.status_code} - Process time: {process_time:.3f}s")

        return response

    except Exception as e:
        # Calculate processing time for error responses
        process_time = time.time() - start_time

        logger.error(f"Error in request processing: {str(e)} - Process time: {process_time:.3f}s")
        raise