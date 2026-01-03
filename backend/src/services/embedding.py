"""
Embedding service for the RAG Agent system.

This module provides functionality to convert text to embeddings using Cohere.
"""

import cohere
from typing import List
from src.config.settings import settings


class EmbeddingService:
    """
    Service class for generating text embeddings using Cohere.
    """

    def __init__(self):
        """
        Initialize the embedding service with Cohere client.
        """
        self.client = cohere.Client(settings.cohere_api_key)

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text string.

        Args:
            text: The text to embed

        Returns:
            A list of floats representing the embedding vector
        """
        response = self.client.embed(
            texts=[text],
            model="embed-english-v3.0",  # Using Cohere's English embedding model
            input_type="search_query"  # Specify the input type for better embeddings
        )
        return response.embeddings[0]

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple text strings.

        Args:
            texts: A list of texts to embed

        Returns:
            A list of embedding vectors (each vector is a list of floats)
        """
        if not texts:
            return []

        response = self.client.embed(
            texts=texts,
            model="embed-english-v3.0",
            input_type="search_document"  # Using search_document for document chunks
        )
        return response.embeddings