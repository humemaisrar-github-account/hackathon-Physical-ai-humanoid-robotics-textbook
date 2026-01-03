from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from src.models.query import Query
from src.models.content_chunk import ContentChunk


class RetrievalResult(BaseModel):
    """
    Model representing the top-K semantically relevant content chunks returned in response to a query with associated scores.
    """
    query: Query = Field(..., description="The original query that generated this result")
    chunks: List[ContentChunk] = Field(..., description="The retrieved content chunks")
    scores: List[float] = Field(..., description="Similarity scores for each chunk")
    retrieval_time_ms: float = Field(..., description="Time taken to retrieve the results")
    total_results: int = Field(..., description="Total number of results found before top-K filtering")

    @field_validator('scores')
    def validate_scores(cls, v):
        """
        Validate that scores are between 0 and 1 (similarity scores).
        """
        for score in v:
            if not 0 <= score <= 1:
                raise ValueError('All scores must be between 0 and 1')
        return v

    @field_validator('retrieval_time_ms')
    def validate_retrieval_time(cls, v):
        """
        Validate that retrieval time is positive.
        """
        if v < 0:
            raise ValueError('Retrieval time must be positive')
        return v

    @field_validator('total_results')
    def validate_total_results(cls, v):
        """
        Validate that total results is non-negative.
        """
        if v < 0:
            raise ValueError('Total results cannot be negative')
        return v