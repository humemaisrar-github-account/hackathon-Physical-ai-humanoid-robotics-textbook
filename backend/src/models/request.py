"""
Request and response models for the RAG Agent API.

This module defines Pydantic models for API requests, responses, and related data structures.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid


class SourceReference(BaseModel):
    """
    Model for source references in the response.

    Represents a document excerpt that was used to generate the agent's response.
    """
    content: str = Field(
        ...,
        description="Excerpt from the source document",
        example="Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience..."
    )
    metadata: Dict[str, Any] = Field(
        ...,
        description="Metadata about the source",
        example={
            "url": "https://example.com/book/chapter1",
            "section_title": "Introduction to Machine Learning",
            "page_number": 42
        }
    )
    relevance_score: float = Field(
        ...,
        description="Relevance score of the source to the query",
        ge=0.0,
        le=1.0,
        example=0.85
    )


class QueryRequest(BaseModel):
    """
    Request model for the /query endpoint.

    Represents a user's question and optional parameters for the RAG agent.
    """
    question: str = Field(
        ...,
        description="The user's question about book content",
        min_length=1,
        max_length=1000,
        example="What are the key principles of machine learning?"
    )
    top_k: Optional[int] = Field(
        5,
        description="Number of documents to retrieve (default: 5)",
        ge=1,
        le=20,
        example=5
    )
    include_sources: bool = Field(
        True,
        description="Whether to include source citations in response (default: true)",
        example=True
    )


class QueryResponse(BaseModel):
    """
    Response model for the /query endpoint.

    Contains the agent's answer and source references used to generate it.
    """
    answer: str = Field(
        ...,
        description="The agent's answer to the user's question",
        example="The key principles of machine learning include supervised learning, unsupervised learning, and reinforcement learning..."
    )
    sources: List[SourceReference] = Field(
        ...,
        description="List of source references used to generate the answer"
    )
    query_id: str = Field(
        default_factory=lambda: f"query-{uuid.uuid4().hex[:8]}",
        description="Unique identifier for the query",
        example="query-12345abc"
    )