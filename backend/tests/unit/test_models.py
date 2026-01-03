"""
Unit tests for the RAG Agent API models.
"""

import pytest
from src.models.request import QueryRequest, QueryResponse, SourceReference
from src.models.agent import UserQuery, RetrievedDocument, AgentResponse


def test_query_request_validation():
    """Test QueryRequest model validation."""
    # Valid request
    request = QueryRequest(question="What is machine learning?", top_k=5)
    assert request.question == "What is machine learning?"
    assert request.top_k == 5

    # Test question length validation
    with pytest.raises(ValueError):
        QueryRequest(question="", top_k=5)  # Too short

    with pytest.raises(ValueError):
        QueryRequest(question="a" * 1001, top_k=5)  # Too long


def test_source_reference_creation():
    """Test SourceReference model creation."""
    source = SourceReference(
        content="Sample content",
        metadata={"url": "http://example.com"},
        relevance_score=0.85
    )

    assert source.content == "Sample content"
    assert source.metadata["url"] == "http://example.com"
    assert source.relevance_score == 0.85


def test_retrieved_document_creation():
    """Test RetrievedDocument model creation."""
    doc = RetrievedDocument(
        id="test-id",
        content="Sample document content",
        metadata={"section": "Introduction"},
        score=0.9
    )

    assert doc.id == "test-id"
    assert doc.content == "Sample document content"
    assert doc.metadata["section"] == "Introduction"
    assert doc.score == 0.9


def test_user_query_model():
    """Test UserQuery model."""
    user_query = UserQuery(
        question="What are the principles?",
        top_k=3,
        include_sources=True
    )

    assert user_query.question == "What are the principles?"
    assert user_query.top_k == 3
    assert user_query.include_sources is True


if __name__ == "__main__":
    test_query_request_validation()
    test_source_reference_creation()
    test_retrieved_document_creation()
    test_user_query_model()
    print("All tests passed!")