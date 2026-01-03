from typing import Dict, Optional, List
from pydantic import BaseModel, Field, field_validator


class Query(BaseModel):
    """
    Model representing a natural language query for semantic search.
    """
    text: str = Field(..., description="The raw natural language query text")
    embedding: Optional[List[float]] = Field(None, description="The vector representation of the query text")
    filters: Dict = Field(default_factory=dict, description="Optional metadata filters (e.g., by URL or section)")
    top_k: int = Field(3, ge=1, le=100, description="Number of results to retrieve (default: 3-5)")

    @field_validator('text')
    def validate_text(cls, v):
        """
        Validate that the query text is not empty or only whitespace.
        """
        if not v or not v.strip():
            raise ValueError('Query text cannot be empty or only whitespace')
        return v.strip()

    @field_validator('top_k')
    def validate_top_k(cls, v):
        """
        Validate that top_k is a positive integer within the allowed range.
        """
        if v < 1 or v > 100:
            raise ValueError('top_k must be between 1 and 100')
        return v

    @field_validator('filters')
    def validate_filters(cls, v):
        """
        Validate that filters have valid field names and values.
        """
        # Basic validation - ensure filters is a dictionary
        if not isinstance(v, dict):
            raise ValueError('Filters must be a dictionary')

        # Validate specific filter field names if provided
        allowed_fields = {'url', 'section', 'section_hierarchy'}
        for field_name in v.keys():
            if field_name not in allowed_fields:
                raise ValueError(f'Invalid filter field: {field_name}. Allowed fields: {allowed_fields}')

        return v