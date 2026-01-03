"""
Custom exception classes for Qdrant and Cohere specific errors.
"""


class QdrantConnectionError(Exception):
    """
    Raised when there is an issue connecting to the Qdrant service.
    """
    pass


class CohereAPIError(Exception):
    """
    Raised when there is an issue with the Cohere API.
    """
    pass


class VectorSearchError(Exception):
    """
    Raised when there is an error during vector search operations.
    """
    pass


class ConfigurationError(Exception):
    """
    Raised when there is a configuration issue.
    """
    pass


class InvalidQueryError(Exception):
    """
    Raised when a query is invalid or malformed.
    """
    pass


class RetrievalError(Exception):
    """
    Raised when there is a general error during retrieval operations.
    """
    pass


class ValidationError(Exception):
    """
    Raised when validation fails for input parameters.
    """
    pass