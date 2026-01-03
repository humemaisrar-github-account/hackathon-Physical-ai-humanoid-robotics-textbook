"""
Data model classes for the RAG pipeline based on the specification.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class BookPageStatus(str, Enum):
    """Status enum for BookPage states."""
    DISCOVERED = "DISCOVERED"
    CRAWLING = "CRAWLING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"


class TextChunkStatus(str, Enum):
    """Status enum for TextChunk states."""
    PENDING = "PENDING"
    EMBEDDING = "EMBEDDING"
    EMBEDDED = "EMBEDDED"
    FAILED = "FAILED"


class Heading(BaseModel):
    """
    Represents a heading element found on a book page.
    """
    level: int = Field(..., ge=1, le=6, description="HTML heading level (1-6)")
    text: str = Field(..., min_length=1, description="Text content of the heading")
    path: str = Field(..., description="Hierarchical path to this heading (e.g., 'Chapter 1 > Section A > Subsection 1')")
    position: int = Field(..., ge=0, description="Position of the heading in the document")

    class Config:
        schema_extra = {
            "example": {
                "level": 2,
                "text": "Introduction to RAG Systems",
                "path": "Chapter 1 > Introduction to RAG Systems",
                "position": 150
            }
        }

    @validator('level')
    def validate_level(cls, v):
        if v < 1 or v > 6:
            raise ValueError('Heading level must be between 1 and 6')
        return v

    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Heading text cannot be empty')
        return v.strip()


class BookPage(BaseModel):
    """
    Represents a single page from the Docusaurus book that has been crawled.
    """
    url: str = Field(..., description="The full URL of the book page")
    title: str = Field(..., min_length=1, description="The page title extracted from HTML")
    content: str = Field("", description="Raw HTML content of the page (before cleaning)")
    text_content: str = Field("", description="Cleaned text content extracted from the page")
    headings: List[Heading] = Field(default_factory=list, description="All headings found on the page with their hierarchy")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the page was crawled")
    status: BookPageStatus = Field(default=BookPageStatus.DISCOVERED, description="Status of the crawl operation")

    class Config:
        schema_extra = {
            "example": {
                "url": "https://my-book.github.io/chapter1/introduction",
                "title": "Introduction to Chapter 1",
                "content": "<html>...</html>",
                "text_content": "This is the cleaned text content...",
                "headings": [
                    {
                        "level": 2,
                        "text": "Introduction",
                        "path": "Chapter 1 > Introduction",
                        "position": 100
                    }
                ],
                "created_at": "2023-12-16T10:30:00",
                "status": "SUCCESS"
            }
        }

    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @validator('content')
    def validate_content(cls, v, values):
        # If status is SUCCESS, content should not be empty
        if values.get('status') == BookPageStatus.SUCCESS and not v:
            raise ValueError('Content must be non-empty for successful crawls')
        return v


class TextChunk(BaseModel):
    """
    A segment of text content that has been chunked according to token limits.
    """
    chunk_id: str = Field(..., description="Unique identifier for this chunk")
    page_url: str = Field(..., description="URL of the source page")
    heading_path: str = Field("", description="Hierarchical path of headings for context")
    content_raw: str = Field(..., min_length=1, description="The raw text content of this chunk")
    token_count: int = Field(..., ge=100, le=1000, description="Number of tokens in this chunk")
    overlap_with_previous: str = Field("", description="Overlapping content with previous chunk (if applicable)")
    overlap_with_next: str = Field("", description="Overlapping content with next chunk (if applicable)")
    position_in_page: int = Field(0, ge=0, description="Position of this chunk in the original page")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the chunk")
    status: TextChunkStatus = Field(default=TextChunkStatus.PENDING, description="Processing status of this chunk")

    class Config:
        schema_extra = {
            "example": {
                "chunk_id": "chunk_001_20231216",
                "page_url": "https://my-book.github.io/chapter1/introduction",
                "heading_path": "Chapter 1 > Introduction",
                "content_raw": "This is a sample text chunk with important information...",
                "token_count": 350,
                "overlap_with_previous": "",
                "overlap_with_next": "This continues from the previous chunk...",
                "position_in_page": 0,
                "metadata": {
                    "section": "introduction",
                    "keywords": ["RAG", "AI", "search"]
                },
                "status": "PENDING"
            }
        }

    @validator('chunk_id')
    def validate_chunk_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Chunk ID cannot be empty')
        return v.strip()

    @validator('page_url')
    def validate_page_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Page URL must start with http:// or https://')
        return v

    @validator('content_raw')
    def validate_content_raw(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()

    @validator('token_count')
    def validate_token_count(cls, v):
        # According to spec: 300-500 tokens with some flexibility
        if v < 100 or v > 1000:
            raise ValueError('Token count must be between 100 and 1000 tokens')
        return v

    @validator('position_in_page')
    def validate_position_in_page(cls, v):
        if v < 0:
            raise ValueError('Position in page cannot be negative')
        return v


class EmbeddingVector(BaseModel):
    """
    A vector representation of a text chunk generated by the embedding model.
    """
    chunk_id: str = Field(..., description="Reference to the source TextChunk")
    vector: List[float] = Field(..., description="The embedding vector (dimension depends on model)")
    model_name: str = Field("embed-english-v3.0", description="Name of the model used for embedding")
    model_version: str = Field("", description="Version of the model used")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the embedding was generated")
    text_chunk: Optional[TextChunk] = Field(None, description="The original text chunk that was embedded")

    class Config:
        schema_extra = {
            "example": {
                "chunk_id": "chunk_001_20231216",
                "vector": [0.1, 0.2, 0.3, 0.4, 0.5],  # Example vector (actual will be much longer)
                "model_name": "embed-english-v3.0",
                "model_version": "3.0.0",
                "created_at": "2023-12-16T10:30:00",
                "text_chunk": {
                    "chunk_id": "chunk_001_20231216",
                    "page_url": "https://my-book.github.io/chapter1/introduction",
                    "content_raw": "This is a sample text chunk...",
                    "token_count": 350
                }
            }
        }

    @validator('chunk_id')
    def validate_chunk_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Chunk ID cannot be empty')
        return v.strip()

    @validator('vector')
    def validate_vector(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Vector cannot be empty')
        # Basic check - vectors should have reasonable length (Cohere embeddings are typically 1024+ dimensions)
        if len(v) < 10:
            raise ValueError('Vector seems too short - Cohere embeddings are typically longer')
        return v

    @validator('model_name')
    def validate_model_name(cls, v):
        valid_models = ["embed-english-v3.0", "embed-multilingual-v3.0"]
        if v not in valid_models:
            raise ValueError(f'Model name must be one of {valid_models}')
        return v


class QdrantRecord(BaseModel):
    """
    A record as stored in the Qdrant vector database.
    """
    id: str = Field(..., description="Unique identifier in Qdrant (same as chunk_id)")
    vector: List[float] = Field(..., description="The embedding vector")
    payload: Dict[str, Any] = Field(..., description="Metadata stored with the vector in Qdrant")
    created_at: datetime = Field(default_factory=datetime.now, description="When the record was stored in Qdrant")

    class Config:
        schema_extra = {
            "example": {
                "id": "chunk_001_20231216",
                "vector": [0.1, 0.2, 0.3, 0.4, 0.5],  # Example vector
                "payload": {
                    "page_url": "https://my-book.github.io/chapter1/introduction",
                    "heading_path": "Chapter 1 > Introduction",
                    "content_raw": "This is a sample text chunk...",
                    "chunk_id": "chunk_001_20231216",
                    "token_count": 350,
                    "position_in_page": 0
                },
                "created_at": "2023-12-16T10:30:00"
            }
        }

    @validator('id')
    def validate_id(cls, v):
        if not v or not v.strip():
            raise ValueError('ID cannot be empty')
        return v.strip()

    @validator('vector')
    def validate_qdrant_vector(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Vector cannot be empty')
        return v

    @validator('payload')
    def validate_payload(cls, v):
        required_fields = ['page_url', 'heading_path', 'content_raw', 'chunk_id', 'token_count']
        for field in required_fields:
            if field not in v:
                raise ValueError(f'Payload must contain required field: {field}')
        return v


# Utility functions for creating model instances
def create_book_page(url: str, title: str) -> BookPage:
    """
    Create a BookPage instance with default values.

    Args:
        url: URL of the book page
        title: Title of the book page

    Returns:
        BookPage: New BookPage instance
    """
    return BookPage(url=url, title=title)


def create_text_chunk(chunk_id: str, page_url: str, content: str, token_count: int) -> TextChunk:
    """
    Create a TextChunk instance with default values.

    Args:
        chunk_id: Unique identifier for the chunk
        page_url: URL of the source page
        content: Raw content of the chunk
        token_count: Number of tokens in the chunk

    Returns:
        TextChunk: New TextChunk instance
    """
    return TextChunk(
        chunk_id=chunk_id,
        page_url=page_url,
        content_raw=content,
        token_count=token_count
    )


def create_embedding_vector(chunk_id: str, vector: List[float], model_name: str = "embed-english-v3.0") -> EmbeddingVector:
    """
    Create an EmbeddingVector instance with default values.

    Args:
        chunk_id: Reference to the source TextChunk
        vector: The embedding vector
        model_name: Name of the model used for embedding

    Returns:
        EmbeddingVector: New EmbeddingVector instance
    """
    return EmbeddingVector(
        chunk_id=chunk_id,
        vector=vector,
        model_name=model_name
    )


def create_qdrant_record(chunk_id: str, vector: List[float], payload: Dict[str, Any]) -> QdrantRecord:
    """
    Create a QdrantRecord instance with default values.

    Args:
        chunk_id: Unique identifier in Qdrant
        vector: The embedding vector
        payload: Metadata to store with the vector

    Returns:
        QdrantRecord: New QdrantRecord instance
    """
    return QdrantRecord(
        id=chunk_id,
        vector=vector,
        payload=payload
    )