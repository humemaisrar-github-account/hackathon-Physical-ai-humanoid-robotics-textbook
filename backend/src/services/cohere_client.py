import cohere
import logging
from typing import List
from src.lib.config import Config


class CohereService:
    """
    Service class to manage Cohere client for embedding generation.
    """

    def __init__(self):
        """
        Initialize Cohere client with API key from configuration.
        """
        api_key = Config.get_cohere_config()
        if not api_key:
            raise ValueError("COHERE_API_KEY is not set in environment variables")

        self.client = cohere.Client(api_key)
        self.model = "embed-english-v3.0"  # Using the same model as spec-1

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embed(
                texts=texts,
                model=self.model,
                input_type="search_query"  # Using search_query as this is for retrieval
            )
            return response.embeddings
        except Exception as e:
            logging.error(f"Error generating embeddings: {str(e)}")
            raise

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text string to embed

        Returns:
            Embedding vector
        """
        embeddings = self.generate_embeddings([text])
        return embeddings[0] if embeddings else []