"""
Agent-related models for the RAG Agent system.

This module defines models for agent configuration, responses, and internal data structures.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from .request import SourceReference


class UserQuery(BaseModel):
    """
    Represents a question submitted by a user about book content.
    """
    question: str = Field(
        ...,
        description="The text of the user's question",
        min_length=1,
        max_length=1000,
        example="What are the key principles of machine learning?"
    )
    top_k: int = Field(
        5,
        description="Number of documents to retrieve (default: 5, range: 1-20)",
        ge=1,
        le=20,
        example=5
    )
    include_sources: bool = Field(
        True,
        description="Whether to include source citations in response (default: true)",
        example=True
    )


class RetrievedDocument(BaseModel):
    """
    Book content chunk retrieved from Qdrant that is relevant to the query.
    """
    id: str = Field(
        ...,
        description="Unique identifier for the document chunk",
        example="doc-12345-abcde"
    )
    content: str = Field(
        ...,
        description="The text content of the chunk",
        example="Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience..."
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the document"
    )
    score: float = Field(
        ...,
        description="Similarity score to the query",
        ge=0.0,
        le=1.0,
        example=0.85
    )


class AgentResponse(BaseModel):
    """
    The generated answer based on retrieved context with source references.
    """
    answer: str = Field(
        ...,
        description="The agent's response to the user's question"
    )
    sources: List[RetrievedDocument] = Field(
        ...,
        description="Documents used to generate the response"
    )
    retrieval_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Information about the retrieval process"
    )