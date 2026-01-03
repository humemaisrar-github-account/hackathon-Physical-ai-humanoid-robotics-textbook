from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Configuration
    api_title: str = "RAG Agent API"
    api_description: str = "API for the Retrieval-Augmented Generation agent that answers questions about book content"
    api_version: str = "1.0.0"

    # OpenAI Configuration (for compatibility)
    openai_api_key: Optional[str] = None

    # OpenRouter Configuration
    openrouter_api_key: str

    # Cohere Configuration
    cohere_api_key: str

    # Qdrant Configuration
    qdrant_url: str
    qdrant_api_key: str

    # Additional Qdrant Configuration (from existing .env)
    qdrant_host: Optional[str] = None
    qdrant_collection: Optional[str] = "book_content_chunks"
    qdrant_collection_name: Optional[str] = "book_content_chunks"

    # Agent Configuration
    agent_timeout: int = 30  # seconds
    top_k_default: int = 5
    top_k_min: int = 1
    top_k_max: int = 20

    # Application Configuration
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # Additional Configuration (from existing .env)
    book_base_url: Optional[str] = "https://physical-ai-humans-text-five.vercel.app/"
    token_min: Optional[int] = 300
    token_max: Optional[int] = 500
    chunk_overlap_percent: Optional[int] = 15
    cohere_model: Optional[str] = "embed-english-v3.0"
    batch_size_embedding: Optional[int] = 10
    batch_size_qdrant: Optional[int] = 100
    crawl_delay: Optional[int] = 1
    api_key: Optional[str] = None  # For API authentication
    gemini_api_key: Optional[str] = ""  # Added for compatibility

    class Config:
        env_file = ".env"
        # Allow extra fields from .env that are not defined in the model
        extra = "allow"


# Create a single instance of settings
settings = Settings()