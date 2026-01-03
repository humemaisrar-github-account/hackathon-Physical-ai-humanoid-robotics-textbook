import time
from typing import List, Optional, Dict, Any
from src.models.query import Query
from src.models.content_chunk import ContentChunk
from src.models.retrieval_result import RetrievalResult
from src.models.metadata_filter import MetadataFilter
from src.services.qdrant_client import QdrantService
from src.services.cohere_client import CohereService
from src.lib.logger import log_performance, log_retrieval_metrics, setup_logger
from src.lib.exceptions import RetrievalError, VectorSearchError, QdrantConnectionError, CohereAPIError, InvalidQueryError


class RetrievalService:
    """
    Service class to handle semantic retrieval operations using Qdrant and Cohere.
    """

    def __init__(self):
        """
        Initialize the retrieval service with Qdrant and Cohere clients.
        """
        self.qdrant_service = QdrantService()
        self.cohere_service = CohereService()
        self.logger = setup_logger(__name__)

    def connect_to_qdrant(self) -> bool:
        """
        Test connection to Qdrant server.

        Returns:
            bool: True if connection is successful, False otherwise
        """
        return self.qdrant_service.connect_to_qdrant()

    def query_embedding(self, query_text: str) -> List[float]:
        """
        Generate embedding for the query text using Cohere.

        Args:
            query_text: The natural language query text

        Returns:
            Embedding vector for the query
        """
        start_time = time.time()
        try:
            embedding = self.cohere_service.embed_text(query_text)
            log_performance("Query embedding generation", start_time)
            return embedding
        except Exception as e:
            log_performance("Query embedding generation", start_time)
            self.logger.error(f"Error generating embedding for query: {str(e)}")
            raise RetrievalError(f"Failed to generate embedding: {str(e)}")

    def vector_search(self, query_embedding: List[float], top_k: int = 3, filters: Optional[Dict] = None):
        """
        Perform vector search in Qdrant to find similar content.

        Args:
            query_embedding: The embedding vector to search for
            top_k: Number of results to return
            filters: Optional metadata filters

        Returns:
            Search results from Qdrant
        """
        start_time = time.time()
        try:
            results = self.qdrant_service.search_vectors(
                vector=query_embedding,
                top_k=top_k,
                filters=filters
            )
            log_performance("Vector search", start_time)
            return results
        except Exception as e:
            log_performance("Vector search", start_time)
            self.logger.error(f"Error during vector search: {str(e)}")
            raise VectorSearchError(f"Failed to perform vector search: {str(e)}")

    def context_reconstruction(self, search_results) -> List[Dict[str, Any]]:
        """
        Reconstruct context from search results to return original text, URL, section hierarchy, and chunk IDs.

        Args:
            search_results: Results from Qdrant vector search

        Returns:
            List of reconstructed content chunks with metadata
        """
        reconstructed_chunks = []

        # Handle different result formats based on the Qdrant client version
        # For newer query_points API, results are in search_results.points
        points = getattr(search_results, 'points', search_results)

        for result in points:
            try:
                # Extract payload data - handle both old and new API formats
                if hasattr(result, 'payload'):
                    # New API format
                    payload = result.payload or {}
                elif hasattr(result, 'dict()'):
                    # If it's a model object
                    payload = getattr(result, 'payload', {}) or {}
                else:
                    # Old format or dict
                    payload = result.get('payload', {}) if isinstance(result, dict) else {}

                # Extract metadata from payload - handle both nested and flat structures
                metadata = payload if isinstance(payload, dict) else {}

                # Extract fields with fallback options for different payload structures
                # Try nested metadata structure first, then flat structure
                text = (
                    metadata.get('metadata', {}).get('text', '') or
                    metadata.get('text', '') or
                    metadata.get('content', '') or
                    ''
                )

                url = (
                    metadata.get('metadata', {}).get('url', '') or
                    metadata.get('url', '') or
                    metadata.get('source', '') or
                    metadata.get('source_url', '') or
                    ''
                )

                section_hierarchy = (
                    metadata.get('metadata', {}).get('section_hierarchy', []) or
                    metadata.get('section_hierarchy', []) or
                    metadata.get('sections', []) or
                    []
                )

                chunk_id = (
                    metadata.get('metadata', {}).get('chunk_id', '') or
                    metadata.get('chunk_id', '') or
                    metadata.get('id', '') or
                    ''
                )

                position = (
                    metadata.get('metadata', {}).get('position') or
                    metadata.get('position') or
                    metadata.get('idx', 0) or
                    0
                )

                # Create content chunk from result - only if text and url are not empty
                if text and url:
                    chunk_data = {
                        'id': getattr(result, 'id', result.get('id', '')) if isinstance(result, dict) else getattr(result, 'id', ''),
                        'text': text,
                        'url': url,
                        'section_hierarchy': section_hierarchy,
                        'chunk_id': chunk_id,
                        'position': position
                    }

                    reconstructed_chunks.append(chunk_data)
                else:
                    # Log when we skip chunks due to missing text or url
                    self.logger.debug(f"Skipping chunk due to missing text or url: text_len={len(text)}, url_len={len(url)}")
                    continue

            except Exception as e:
                self.logger.warning(f"Error reconstructing context for result: {str(e)}")
                continue

        return reconstructed_chunks

    def retrieve(self, query: Query) -> RetrievalResult:
        """
        Main retrieval method that orchestrates the entire process.

        Args:
            query: Query object containing the search parameters

        Returns:
            RetrievalResult containing the search results with metadata
        """
        start_time = time.time()

        try:
            # Validate query
            if not query.text or not query.text.strip():
                raise InvalidQueryError("Query text cannot be empty")

            # Check connection to Qdrant
            if not self.connect_to_qdrant():
                raise QdrantConnectionError("Cannot connect to Qdrant for retrieval")

            # Generate embedding for the query text
            query_embedding = self.query_embedding(query.text)

            # Perform vector search
            search_results = self.vector_search(
                query_embedding=query_embedding,
                top_k=query.top_k,
                filters=query.filters
            )

            # Reconstruct context from search results
            reconstructed_chunks = self.context_reconstruction(search_results)

            # Calculate retrieval time
            retrieval_time_ms = (time.time() - start_time) * 1000

            # Extract scores from search results - handle different API versions
            scores = []
            points = getattr(search_results, 'points', search_results)
            for result in points:
                if hasattr(result, 'score'):
                    # New API format
                    score = result.score
                elif hasattr(result, 'dict()'):
                    # If it's a model object with different attribute name
                    score = getattr(result, 'score', 0)
                else:
                    # Old format or dict
                    score = result.get('score', 0) if isinstance(result, dict) else 0
                scores.append(score)

            # Calculate average score for logging
            avg_score = sum(scores) / len(scores) if scores else 0

            # Create content chunk objects
            content_chunks = []
            for chunk_data in reconstructed_chunks:
                try:
                    content_chunk = ContentChunk(**chunk_data)
                    content_chunks.append(content_chunk)
                except Exception as chunk_error:
                    self.logger.warning(f"Error creating content chunk: {str(chunk_error)}")
                    continue  # Skip invalid chunks but continue processing

            # Create and return retrieval result
            # Get the total number of results from the search_results object
            total_search_results = len(getattr(search_results, 'points', search_results)) if hasattr(search_results, '__len__') else 0

            result = RetrievalResult(
                query=query,
                chunks=content_chunks,
                scores=scores[:len(content_chunks)],  # Only include scores for valid chunks
                retrieval_time_ms=retrieval_time_ms,
                total_results=total_search_results
            )

            # Log retrieval metrics
            log_retrieval_metrics(
                query=query.text,
                num_results=len(content_chunks),
                retrieval_time_ms=retrieval_time_ms,
                avg_score=avg_score,
                scores=scores[:len(content_chunks)]
            )

            return result

        except QdrantConnectionError:
            retrieval_time_ms = (time.time() - start_time) * 1000
            self.logger.error("Qdrant connection error during retrieval")
            raise
        except CohereAPIError:
            retrieval_time_ms = (time.time() - start_time) * 1000
            self.logger.error("Cohere API error during retrieval")
            raise
        except InvalidQueryError:
            retrieval_time_ms = (time.time() - start_time) * 1000
            self.logger.error("Invalid query error during retrieval")
            raise
        except Exception as e:
            retrieval_time_ms = (time.time() - start_time) * 1000
            self.logger.error(f"Error during retrieval: {str(e)}")
            raise RetrievalError(f"Retrieval failed after {retrieval_time_ms:.2f}ms: {str(e)}")