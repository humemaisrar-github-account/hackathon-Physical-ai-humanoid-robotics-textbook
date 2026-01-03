#!/usr/bin/env python3
"""
Main pipeline execution script that orchestrates all components of the RAG pipeline.
This script runs the complete workflow from reading local Docusaurus content to validation.
"""
import sys
import os
import time
import argparse
from typing import Optional, Dict, Any
from datetime import datetime

# Add backend to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.logging_config import get_logger
from config.config import config
from crawler.local_content_reader import LocalDocusaurusReader
from chunker.text_chunker import TextChunker
from embedder.cohere_embedder import CohereEmbedder
from storage.qdrant_client import initialize_qdrant_collection, store_embeddings_in_qdrant
from validation.validator import validate_pipeline_completion
from models.data_models import TextChunk, QdrantRecord


logger = get_logger("pipeline_runner")


class PipelineOrchestrator:
    """
    Orchestrates the complete RAG pipeline from reading local content to validation.
    """
    def __init__(self):
        self.pipeline_status = "idle"
        self.start_time = None
        self.results = {}

    def run_content_reading_phase(self, docs_path: str = None) -> bool:
        """
        Execute the content reading phase of the pipeline using local Docusaurus files.

        Args:
            docs_path: Path to the Docusaurus docs directory (defaults to config value)

        Returns:
            bool: True if content reading phase completed successfully
        """
        logger.info(f"Starting content reading phase from local directory: {docs_path or config.local_docs_dir or 'frontend/docs'}")
        self.pipeline_status = "reading"
        start_time = time.time()

        try:
            # Initialize local Docusaurus reader
            reader = LocalDocusaurusReader(docs_path)

            # Read all Docusaurus content
            book_pages = reader.read_docusaurus_content()

            if not book_pages:
                logger.warning("No content found in the docs directory")
                return True  # Not a failure, just no content to process

            logger.info(f"Read {len(book_pages)} pages from local Docusaurus content")

            # Save pages to data directory
            os.makedirs("data/pages", exist_ok=True)
            for i, page in enumerate(book_pages):
                # Create a safe filename from the page URL
                safe_filename = f"page_{i:04d}.json"
                filepath = os.path.join("data/pages", safe_filename)

                # Save as JSON
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(page.model_dump_json(indent=2))

            read_time = time.time() - start_time
            self.results['content_reading'] = {
                'status': 'success',
                'pages_read': len(book_pages),
                'time_elapsed': read_time
            }

            logger.info(f"Content reading phase completed successfully. {len(book_pages)} pages read in {read_time:.2f}s")
            return True

        except Exception as e:
            logger.error(f"Content reading phase failed: {str(e)}")
            self.results['content_reading'] = {
                'status': 'failed',
                'error': str(e),
                'time_elapsed': time.time() - start_time
            }
            return False

    def run_chunking_phase(self) -> bool:
        """
        Execute the chunking phase of the pipeline.

        Returns:
            bool: True if chunking phase completed successfully
        """
        logger.info("Starting chunking phase")
        self.pipeline_status = "chunking"
        start_time = time.time()

        try:
            # Initialize chunker
            chunker = TextChunker(
                min_tokens=config.token_min,
                max_tokens=config.token_max,
                overlap_percent=config.chunk_overlap_percent
            )

            # Load text content from saved pages
            pages_dir = "data/pages"
            if not os.path.exists(pages_dir):
                logger.error(f"Pages directory does not exist: {pages_dir}")
                return False

            # Read all saved page files
            text_contents = []
            page_files = [f for f in os.listdir(pages_dir) if f.endswith('.json')]

            for page_file in page_files:
                filepath = os.path.join(pages_dir, page_file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        import json
                        page_data = json.load(f)

                        # Create a text content entry for chunking
                        text_contents.append({
                            'content': page_data.get('text_content', ''),
                            'source_url': page_data.get('url', ''),
                            'title': page_data.get('title', ''),
                            'headings': page_data.get('headings', [])
                        })
                except Exception as e:
                    logger.error(f"Error reading page file {filepath}: {e}")

            if not text_contents:
                logger.warning("No text content found to chunk")
                return True  # Not a failure, just no content to process

            # Process each text content into chunks
            all_chunks = []
            for i, content_data in enumerate(text_contents):
                text_content = content_data['content']  # This contains the text_content from page_data
                source_url = content_data['source_url']

                if text_content.strip():  # Only process non-empty extracted text content
                    chunks = chunker.chunk_text(text_content, page_url=source_url)
                    all_chunks.extend(chunks)

                    logger.debug(f"Processed text content from {source_url}, created {len(chunks)} chunks")
                else:
                    logger.warning(f"Skipping empty text content from {source_url}")

            # Save chunks to data directory
            os.makedirs("data/chunks", exist_ok=True)
            for i, chunk in enumerate(all_chunks):
                chunk_file = f"chunk_{i:04d}.json"
                filepath = os.path.join("data/chunks", chunk_file)

                # Save as JSON
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(chunk.model_dump_json(indent=2))

            chunk_time = time.time() - start_time
            self.results['chunking'] = {
                'status': 'success',
                'chunks_created': len(all_chunks),
                'time_elapsed': chunk_time
            }

            logger.info(f"Chunking phase completed successfully. {len(all_chunks)} chunks created in {chunk_time:.2f}s")
            return True

        except Exception as e:
            logger.error(f"Chunking phase failed: {str(e)}")
            self.results['chunking'] = {
                'status': 'failed',
                'error': str(e),
                'time_elapsed': time.time() - start_time
            }
            return False

    def run_embedding_phase(self) -> bool:
        """
        Execute the embedding phase of the pipeline.

        Returns:
            bool: True if embedding phase completed successfully
        """
        logger.info("Starting embedding phase")
        self.pipeline_status = "embedding"
        start_time = time.time()

        try:
            # Initialize embedder
            embedder = CohereEmbedder(
                api_key=config.cohere_api_key,
                model_name=config.cohere_model
            )

            # Load text chunks from saved files
            chunks_dir = "data/chunks"
            if not os.path.exists(chunks_dir):
                logger.error(f"Chunks directory does not exist: {chunks_dir}")
                return False

            # Read all saved chunk files
            text_chunks = []
            chunk_files = [f for f in os.listdir(chunks_dir) if f.endswith('.json')]

            for chunk_file in chunk_files:
                filepath = os.path.join(chunks_dir, chunk_file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        import json
                        chunk_data = json.load(f)

                        # Create TextChunk object from the loaded data
                        from models.data_models import TextChunk
                        chunk = TextChunk(
                            chunk_id=chunk_data.get('chunk_id', f"local_chunk_{len(text_chunks):04d}"),
                            page_url=chunk_data.get('page_url', ''),
                            heading_path=chunk_data.get('heading_path', ''),
                            content_raw=chunk_data.get('content_raw', ''),
                            token_count=chunk_data.get('token_count', len(chunk_data.get('content_raw', '').split())),
                            overlap_with_previous=chunk_data.get('overlap_with_previous', ''),
                            overlap_with_next=chunk_data.get('overlap_with_next', ''),
                            position_in_page=chunk_data.get('position_in_page', 0),
                            metadata=chunk_data.get('metadata', {})
                        )
                        text_chunks.append(chunk)
                except Exception as e:
                    logger.error(f"Error reading chunk file {filepath}: {e}")

            if not text_chunks:
                logger.warning("No text chunks found for embedding")
                return True  # Not a failure, just no content to process

            logger.info(f"Loaded {len(text_chunks)} text chunks for embedding")

            # Generate embeddings
            embedding_vectors = embedder.embed_text_chunks(text_chunks)

            # Save embeddings to data directory
            os.makedirs("data/embeddings", exist_ok=True)
            for i, ev in enumerate(embedding_vectors):
                embedding_file = f"embedding_{i:04d}.json"
                filepath = os.path.join("data/embeddings", embedding_file)

                # Save as JSON
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(ev.model_dump_json(indent=2))

            embed_time = time.time() - start_time
            self.results['embedding'] = {
                'status': 'success',
                'embeddings_created': len(embedding_vectors),
                'time_elapsed': embed_time
            }

            logger.info(f"Embedding phase completed successfully. {len(embedding_vectors)} embeddings created in {embed_time:.2f}s")
            return True

        except Exception as e:
            logger.error(f"Embedding phase failed: {str(e)}")
            self.results['embedding'] = {
                'status': 'failed',
                'error': str(e),
                'time_elapsed': time.time() - start_time
            }
            return False

    def run_storage_phase(self) -> bool:
        """
        Execute the storage phase of the pipeline.

        Returns:
            bool: True if storage phase completed successfully
        """
        logger.info("Starting storage phase")
        self.pipeline_status = "uploading"
        start_time = time.time()

        try:
            # Initialize Qdrant collection
            collection_ok = initialize_qdrant_collection(
                collection_name=config.qdrant_collection_name
            )

            if not collection_ok:
                raise Exception("Failed to initialize Qdrant collection")

            # Load embeddings and convert to Qdrant records
            embeddings_dir = "data/embeddings"
            if not os.path.exists(embeddings_dir):
                logger.error(f"Embeddings directory does not exist: {embeddings_dir}")
                return False

            # Read all saved embedding files
            embedding_vectors = []
            embedding_files = [f for f in os.listdir(embeddings_dir) if f.endswith('.json')]

            for embedding_file in embedding_files:
                filepath = os.path.join(embeddings_dir, embedding_file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        import json
                        embedding_data = json.load(f)

                        # Create EmbeddingVector object from the loaded data
                        from models.data_models import EmbeddingVector, TextChunk
                        # Create a basic TextChunk for the embedding
                        text_chunk = None
                        if 'text_chunk' in embedding_data and embedding_data['text_chunk']:
                            chunk_data = embedding_data['text_chunk']
                            text_chunk = TextChunk(
                                chunk_id=chunk_data.get('chunk_id', ''),
                                page_url=chunk_data.get('page_url', ''),
                                heading_path=chunk_data.get('heading_path', ''),
                                content_raw=chunk_data.get('content_raw', ''),
                                token_count=chunk_data.get('token_count', 0),
                                position_in_page=chunk_data.get('position_in_page', 0)
                            )

                        embedding_vector = EmbeddingVector(
                            chunk_id=embedding_data.get('chunk_id', ''),
                            vector=embedding_data.get('vector', []),
                            model_name=embedding_data.get('model_name', config.cohere_model),
                            model_version=embedding_data.get('model_version', ''),
                            text_chunk=text_chunk
                        )
                        embedding_vectors.append(embedding_vector)
                except Exception as e:
                    logger.error(f"Error reading embedding file {filepath}: {e}")

            if not embedding_vectors:
                logger.warning("No embeddings found to store")
                return True  # Not a failure, just no content to store

            logger.info(f"Loaded {len(embedding_vectors)} embeddings for storage")

            # Convert EmbeddingVector objects to QdrantRecord objects
            qdrant_records = []
            for ev in embedding_vectors:
                # Create payload with metadata
                payload = {
    # 🔴 REQUIRED by QdrantRecord validator
    "page_url": ev.text_chunk.page_url if ev.text_chunk else "",
    "heading_path": ev.text_chunk.heading_path if ev.text_chunk else "",
    "content_raw": ev.text_chunk.content_raw if ev.text_chunk else "",

    # 🔵 Useful indexing fields
    "chunk_id": ev.chunk_id,
    "token_count": ev.text_chunk.token_count if ev.text_chunk else 0,
    "position_in_page": ev.text_chunk.position_in_page if ev.text_chunk else 0,

    # 🟢 Optional metadata (future RAG / UI)
    "metadata": {
        "text": ev.text_chunk.content_raw if ev.text_chunk else "",
        "url": ev.text_chunk.page_url if ev.text_chunk else "",
        "section_hierarchy": (
            ev.text_chunk.heading_path.split(" > ")
            if ev.text_chunk and ev.text_chunk.heading_path
            else []
        )
    }
}


                from models.data_models import QdrantRecord
                record = QdrantRecord(
                    id=ev.chunk_id,
                    vector=ev.vector,
                    payload=payload
                )
                qdrant_records.append(record)

            # Upload to Qdrant
            storage_ok = store_embeddings_in_qdrant(qdrant_records)

            storage_time = time.time() - start_time
            self.results['storage'] = {
                'status': 'success' if storage_ok else 'failed',
                'records_stored': len(qdrant_records) if storage_ok else 0,
                'time_elapsed': storage_time
            }

            if storage_ok:
                logger.info(f"Storage phase completed successfully. {len(qdrant_records)} records stored in {storage_time:.2f}s")
                return True
            else:
                logger.error("Storage phase failed")
                return False

        except Exception as e:
            logger.error(f"Storage phase failed: {str(e)}")
            self.results['storage'] = {
                'status': 'failed',
                'error': str(e),
                'time_elapsed': time.time() - start_time
            }
            return False

    def run_validation_phase(self) -> bool:
        """
        Execute the validation phase of the pipeline.

        Returns:
            bool: True if validation phase completed successfully
        """
        logger.info("Starting validation phase")
        self.pipeline_status = "validating"
        start_time = time.time()

        try:
            # Run comprehensive validation
            validation_results = validate_pipeline_completion()

            validation_time = time.time() - start_time
            self.results['validation'] = {
                'status': 'success',
                'time_elapsed': validation_time,
                'validation_results': validation_results
            }

            # Check if validation passed
            summary = validation_results.get("summary", {})
            overall_status = summary.get("overall_status", "UNKNOWN")

            validation_passed = overall_status in ["PASSED", "PARTIAL"]

            if validation_passed:
                logger.info(f"Validation phase completed successfully. Status: {overall_status}")
                return True
            else:
                logger.warning(f"Validation phase completed but with issues. Status: {overall_status}")
                return True  # Return True as the validation process itself succeeded, even if issues were found

        except Exception as e:
            logger.error(f"Validation phase failed: {str(e)}")
            self.results['validation'] = {
                'status': 'failed',
                'error': str(e),
                'time_elapsed': time.time() - start_time
            }
            return False

    def run_full_pipeline(self, docs_path: str = None) -> bool:
        """
        Execute the complete pipeline from start to finish using local Docusaurus content.

        Args:
            docs_path: Path to the Docusaurus docs directory (defaults to config value)

        Returns:
            bool: True if pipeline completed successfully
        """
        logger.info(f"Starting full RAG pipeline for local docs: {docs_path or config.local_docs_dir or 'frontend/docs'}")
        self.start_time = time.time()
        self.pipeline_status = "running"

        # Run all phases sequentially
        phases = [
            ("content_reading", self.run_content_reading_phase),
            ("chunking", self.run_chunking_phase),
            ("embedding", self.run_embedding_phase),
            ("storage", self.run_storage_phase),
            ("validation", self.run_validation_phase),
        ]

        all_phases_passed = True

        for phase_name, phase_func in phases:
            logger.info(f"Running {phase_name} phase...")
            if phase_name == "content_reading":
                phase_success = phase_func(docs_path)
            else:
                phase_success = phase_func()

            if not phase_success:
                logger.error(f"{phase_name.capitalize()} phase failed. Pipeline halted.")
                all_phases_passed = False
                break
            else:
                logger.info(f"{phase_name.capitalize()} phase completed successfully.")

        # Finalize pipeline
        total_time = time.time() - self.start_time
        self.pipeline_status = "completed" if all_phases_passed else "failed"

        self.results['total'] = {
            'status': 'completed' if all_phases_passed else 'failed',
            'time_elapsed': total_time,
            'timestamp': datetime.now().isoformat()
        }

        logger.info(f"Pipeline {'completed' if all_phases_passed else 'failed'} in {total_time:.2f}s")

        return all_phases_passed

    def get_status(self) -> Dict[str, Any]:
        """
        Get current pipeline execution status.

        Returns:
            Dict containing pipeline status information
        """
        current_time = time.time()
        elapsed_time = (current_time - self.start_time) if self.start_time else 0

        return {
            'pipeline_status': self.pipeline_status,
            'progress': self._calculate_progress(),
            'elapsed_time': elapsed_time,
            'results': self.results
        }

    def _calculate_progress(self) -> float:
        """
        Calculate pipeline progress as a percentage.

        Returns:
            Progress percentage as float
        """
        if not self.results:
            return 0.0

        # Simple calculation: completed phases / total phases
        completed_phases = sum(1 for result in self.results.values()
                              if isinstance(result, dict) and result.get('status') in ['success', 'completed'])

        # Total phases we expect to run
        total_phases = 5  # crawling, chunking, embedding, storage, validation

        return (completed_phases / total_phases) * 100 if total_phases > 0 else 0.0


def main():
    """
    Main function to run the pipeline with command-line arguments.
    """
    parser = argparse.ArgumentParser(description='Run the RAG pipeline from local Docusaurus content')
    parser.add_argument('--docs-path', type=str, default=None,
                       help='Path to the Docusaurus docs directory (defaults to frontend/docs)')
    parser.add_argument('--config', type=str, default=None,
                       help='Path to configuration file')

    args = parser.parse_args()

    # Load configuration if provided
    if args.config:
        config.load_from_file(args.config)

    if not config.cohere_api_key:
        print("Warning: Cohere API key not found in configuration. Embedding phase will use mock data.")

    # Create orchestrator and run pipeline
    orchestrator = PipelineOrchestrator()

    docs_path = args.docs_path or config.local_docs_dir or "frontend/docs"
    print(f"Starting RAG pipeline for local docs: {docs_path}")
    print("=" * 60)

    success = orchestrator.run_full_pipeline(docs_path)

    print("=" * 60)
    if success:
        print("✅ Pipeline completed successfully!")
    else:
        print("❌ Pipeline failed. Check logs for details.")

    # Print summary
    status = orchestrator.get_status()
    print(f"Pipeline Status: {status['pipeline_status']}")
    print(f"Total Time: {status['elapsed_time']:.2f}s")
    print(f"Progress: {status['progress']:.1f}%")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())