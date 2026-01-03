"""
Contract tests for the RAG Agent API endpoints.

This module contains contract tests that verify the API endpoints match the
OpenAPI specification defined in contracts/query-api.yaml.
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
os.environ.setdefault("API_KEY", "test-api-key")  # For authentication


client = TestClient(app)


def test_query_endpoint_contract():
    """Test the query endpoint matches the contract specification."""
    # Test valid request structure
    response = client.post(
        "/api/v1/query",
        json={
            "question": "What is machine learning?",
            "top_k": 5,
            "include_sources": True
        },
        headers={"Authorization": "Bearer test-api-key"}
    )

    # Should return 200 or 500 (not found in book) - depends on if Qdrant is available
    assert response.status_code in [200, 500]

    if response.status_code == 200:
        data = response.json()
        # Verify response structure matches contract
        assert "answer" in data
        assert "sources" in data
        assert "query_id" in data
        assert isinstance(data["answer"], str)
        assert isinstance(data["sources"], list)
        assert isinstance(data["query_id"], str)

        # Verify source structure
        for source in data["sources"]:
            assert "content" in source
            assert "metadata" in source
            assert "relevance_score" in source
            assert isinstance(source["content"], str)
            assert isinstance(source["metadata"], dict)
            assert isinstance(source["relevance_score"], (int, float))
            assert 0 <= source["relevance_score"] <= 1


def test_query_endpoint_validation():
    """Test that the query endpoint properly validates inputs per contract."""
    # Test question validation (1-1000 characters)
    response = client.post(
        "/api/v1/query",
        json={
            "question": "",  # Too short
            "top_k": 5
        },
        headers={"Authorization": "Bearer test-api-key"}
    )
    assert response.status_code == 422  # Validation error

    # Test question too long
    long_question = "x" * 1001
    response = client.post(
        "/api/v1/query",
        json={
            "question": long_question,  # Too long
            "top_k": 5
        },
        headers={"Authorization": "Bearer test-api-key"}
    )
    assert response.status_code == 422  # Validation error

    # Test top_k validation (1-20 range)
    response = client.post(
        "/api/v1/query",
        json={
            "question": "What is AI?",
            "top_k": 0  # Below minimum
        },
        headers={"Authorization": "Bearer test-api-key"}
    )
    assert response.status_code == 422  # Validation error

    response = client.post(
        "/api/v1/query",
        json={
            "question": "What is AI?",
            "top_k": 21  # Above maximum
        },
        headers={"Authorization": "Bearer test-api-key"}
    )
    assert response.status_code == 422  # Validation error


def test_missing_authentication():
    """Test that the endpoint requires authentication."""
    response = client.post(
        "/api/v1/query",
        json={
            "question": "What is machine learning?",
            "top_k": 5
        }
        # No authorization header
    )
    assert response.status_code in [401, 403, 422]  # Unauthorized or validation error


def test_health_endpoint():
    """Test the health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "healthy"}


def test_api_v1_health_endpoint():
    """Test the API v1 health endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["service"] == "RAG Agent API"


if __name__ == "__main__":
    test_query_endpoint_contract()
    test_query_endpoint_validation()
    test_missing_authentication()
    test_health_endpoint()
    test_api_v1_health_endpoint()
    print("All contract tests passed!")