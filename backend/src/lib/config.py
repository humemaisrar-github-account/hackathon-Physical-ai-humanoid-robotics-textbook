import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Configuration class to manage environment variables for Qdrant and Cohere services.
    """

    # Qdrant Configuration
    QDRANT_HOST: str = os.getenv("QDRANT_URL") or os.getenv("QDRANT_HOST", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION", "book_embeddings")

    # Cohere Configuration
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")

    @classmethod
    def validate(cls) -> bool:
        """
        Validate that all required configuration values are present.

        Returns:
            bool: True if all required configurations are set, False otherwise
        """
        required_fields = [
            cls.QDRANT_HOST,
            cls.QDRANT_API_KEY,
            cls.QDRANT_COLLECTION_NAME,
            cls.COHERE_API_KEY
        ]

        return all(field.strip() for field in required_fields)

    @classmethod
    def get_qdrant_config(cls) -> dict:
        """
        Get Qdrant configuration as a dictionary.

        Returns:
            dict: Dictionary containing Qdrant configuration
        """
        return {
            "host": cls.QDRANT_HOST,
            "api_key": cls.QDRANT_API_KEY,
            "collection_name": cls.QDRANT_COLLECTION_NAME
        }

    @classmethod
    def get_cohere_config(cls) -> str:
        """
        Get Cohere API key.

        Returns:
            str: Cohere API key
        """
        return cls.COHERE_API_KEY