"""
Integration tests for the RAG Agent API.
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
import os


# Set up test environment variables
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("COHERE_API_KEY", "test-key")
os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
os.environ.setdefault("QDRANT_API_KEY", "test-key")


client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_api_v1_health_endpoint():
    """Test the API v1 health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "RAG Agent API"}


def test_query_endpoint_invalid_auth():
    """Test that query endpoint requires authentication."""
    response = client.post(
        "/api/v1/query",
        json={"question": "What is AI?"}
    )
    # Should fail due to missing authentication
    assert response.status_code in [401, 422]  # Either auth error or validation error


if __name__ == "__main__":
    test_health_endpoint()
    test_api_v1_health_endpoint()
    test_query_endpoint_invalid_auth()
    print("All integration tests passed!")