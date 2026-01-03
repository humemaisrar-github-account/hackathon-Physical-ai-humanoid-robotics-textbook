"""
Configuration module to handle environment variables and settings for the RAG pipeline.
"""
import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class PipelineConfig(BaseModel):
    """
    Configuration class for the RAG pipeline with validation.
    """
    # Cohere API Configuration
    cohere_api_key: str = Field(..., description="Cohere API key for embedding generation")

    # Qdrant Configuration
    qdrant_url: str = Field(..., description="Qdrant Cloud URL")
    qdrant_api_key: Optional[str] = Field(None, description="Qdrant API key (optional for local instances)")
    qdrant_collection_name: str = Field(default="book_content_chunks", description="Name of the Qdrant collection")

    # Book Configuration
    book_base_url: str = Field(..., description="Base URL of the deployed Docusaurus book")

    # Pipeline Configuration
    token_min: int = Field(default=300, ge=100, le=1000, description="Minimum tokens per chunk")
    token_max: int = Field(default=500, ge=100, le=1000, description="Maximum tokens per chunk")
    chunk_overlap_percent: float = Field(default=15.0, ge=0.0, le=50.0, description="Overlap percentage between chunks")
    cohere_model: str = Field(default="embed-english-v3.0", description="Cohere model to use for embeddings")
    batch_size_embedding: int = Field(default=10, ge=1, le=96, description="Batch size for embedding API calls")
    batch_size_qdrant: int = Field(default=100, ge=1, le=200, description="Batch size for Qdrant uploads")
    crawl_delay: float = Field(default=1.0, ge=0.0, description="Delay in seconds between crawl requests")
    cohere_rate_limit_delay: float = Field(default=1.0, ge=0.0, le=10.0, description="Minimum delay in seconds between Cohere API calls")

    # Directory paths
    data_dir: str = Field(default="data", description="Base directory for data storage")
    pages_dir: str = Field(default="data/pages", description="Directory for crawled pages")
    cleaned_dir: str = Field(default="data/cleaned", description="Directory for cleaned content")
    chunks_dir: str = Field(default="data/chunks", description="Directory for text chunks")
    embeddings_dir: str = Field(default="data/embeddings", description="Directory for embeddings")
    logs_dir: str = Field(default="logs", description="Directory for log files")

    class Config:
        # Allow extra fields but ignore them
        extra = "ignore"


def get_config() -> PipelineConfig:
    """
    Get the pipeline configuration from environment variables.

    Returns:
        PipelineConfig: Configuration object with validated settings
    """
    return PipelineConfig(
        cohere_api_key=os.getenv("COHERE_API_KEY", ""),
        qdrant_url=os.getenv("QDRANT_URL", ""),
        qdrant_api_key=os.getenv("QDRANT_API_KEY"),
        qdrant_collection_name=os.getenv("QDRANT_COLLECTION_NAME", "book_content_chunks"),
        book_base_url=os.getenv("BOOK_BASE_URL", ""),
        token_min=int(os.getenv("TOKEN_MIN", "300")),
        token_max=int(os.getenv("TOKEN_MAX", "500")),
        chunk_overlap_percent=float(os.getenv("CHUNK_OVERLAP_PERCENT", "15.0")),
        cohere_model=os.getenv("COHERE_MODEL", "embed-english-v3.0"),
        batch_size_embedding=int(os.getenv("BATCH_SIZE_EMBEDDING", "10")),
        batch_size_qdrant=int(os.getenv("BATCH_SIZE_QDRANT", "100")),
        crawl_delay=float(os.getenv("CRAWL_DELAY", "1.0")),
        cohere_rate_limit_delay=float(os.getenv("COHERE_RATE_LIMIT_DELAY", "1.0")),
    )


# Global configuration instance
config = get_config()


def validate_config(config: PipelineConfig) -> bool:
    """
    Validate the configuration settings.

    Args:
        config: PipelineConfig object to validate

    Returns:
        bool: True if configuration is valid, False otherwise
    """
    # Check required API keys are not empty
    if not config.cohere_api_key:
        print("Warning: COHERE_API_KEY is not set")
        return False

    if not config.qdrant_url:
        print("Warning: QDRANT_URL is not set")
        return False

    if not config.book_base_url:
        print("Warning: BOOK_BASE_URL is not set")
        return False

    # Check token settings are valid
    if config.token_min > config.token_max:
        print("Error: TOKEN_MIN cannot be greater than TOKEN_MAX")
        return False

    if config.token_min < 100 or config.token_max > 1000:
        print("Error: Token settings out of valid range (100-1000)")
        return False

    # Check overlap percentage is valid
    if config.chunk_overlap_percent < 0 or config.chunk_overlap_percent > 50:
        print("Error: CHUNK_OVERLAP_PERCENT must be between 0 and 50")
        return False

    return True


if __name__ == "__main__":
    # Validate the configuration
    if validate_config(config):
        print("Configuration is valid")
    else:
        print("Configuration has errors - please check environment variables")