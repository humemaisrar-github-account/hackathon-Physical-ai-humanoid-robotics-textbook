from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class ContentChunk(BaseModel):
    """
    Model representing a segment of book content with associated metadata stored in Qdrant.
    """
    id: str = Field(..., description="Unique identifier for the chunk")
    text: str = Field(..., description="The original text content of the chunk")
    url: str = Field(..., description="Source URL where the content originated")
    section_hierarchy: List[str] = Field(default_factory=list, description="Hierarchical path of sections/headers")
    chunk_id: str = Field(..., description="Identifier for the specific chunk within the document")
    position: Optional[int] = Field(None, description="Position order within the original document")

    @field_validator('text')
    def validate_text(cls, v):
        """
        Validate that the text is not empty.
        """
        if not v or not v.strip():
            raise ValueError('Content chunk text cannot be empty')
        return v

    @field_validator('url')
    def validate_url(cls, v):
        """
        Validate that the URL has a valid format.
        """
        if not v:
            raise ValueError('URL cannot be empty')

        # Basic URL validation - check if it starts with http/https
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')

        return v

    @field_validator('id')
    def validate_id(cls, v):
        """
        Validate that the ID is not empty.
        """
        if not v or not v.strip():
            raise ValueError('ID cannot be empty')
        return v

    @field_validator('chunk_id')
    def validate_chunk_id(cls, v):
        """
        Validate that the chunk_id is not empty.
        """
        if not v or not v.strip():
            raise ValueError('Chunk ID cannot be empty')
        return v