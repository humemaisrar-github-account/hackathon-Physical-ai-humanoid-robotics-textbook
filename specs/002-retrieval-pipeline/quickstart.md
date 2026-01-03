# Quickstart: Retrieval Pipeline

**Feature**: 002-retrieval-pipeline
**Date**: 2025-12-29

## Prerequisites

- Python 3.11 or higher
- UV package manager
- Qdrant Cloud account and collection (from Spec-1)
- Cohere API key
- Access to the vector collection created in Spec-1

## Setup

### 1. Environment Setup

```bash
# Navigate to the backend directory
cd backend/

# Install dependencies using UV
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install project dependencies
uv pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the backend directory with the following variables:

```env
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
COHERE_API_KEY=your_cohere_api_key
QDRANT_COLLECTION_NAME=your_collection_name_from_spec1
COHERE_MODEL_NAME=embed-multilingual-v2.0  # Or the model used in Spec-1
TOP_K_DEFAULT=5
```

### 3. Verify Connection

Test the connection to Qdrant and Cohere services:

```bash
python -c "from src.retrieval.vector_search import VectorSearchService; print('Qdrant connection successful')"
python -c "from src.retrieval.embedding_service import EmbeddingService; print('Cohere connection successful')"
```

## Usage Examples

### 1. Basic Query

```python
from src.retrieval.query_processor import QueryProcessor

# Initialize the query processor
processor = QueryProcessor()

# Perform a basic semantic search
query = "Explain the concept of neural networks"
results = processor.search(query, top_k=3)

# Print results
for chunk in results.chunks:
    print(f"Score: {chunk.score}")
    print(f"Text: {chunk.text}")
    print(f"Source: {chunk.source_url}")
    print("---")
```

### 2. Query with Metadata Filtering

```python
from src.retrieval.query_processor import QueryProcessor

processor = QueryProcessor()

# Query with source URL filter
query = "Information about machine learning algorithms"
filters = {
    "source_url": "https://example.com/machine-learning-book/chapter-3"
}

results = processor.search(query, top_k=5, filters=filters)

# Process filtered results
for chunk in results.chunks:
    print(f"Filtered result from: {chunk.source_url}")
    print(f"Content: {chunk.text[:200]}...")
    print("---")
```

### 3. Using the Command-Line Interface

```bash
# Basic search
python -m src.cli.retrieval_cli --query "What is RAG?" --top-k 3

# Search with filters
python -m src.cli.retrieval_cli --query "neural networks" --top-k 5 --filter source_url=https://example.com/book/chapter-2

# Get performance metrics
python -m src.cli.retrieval_cli --query "deep learning basics" --top-k 3 --verbose
```

## Key Components

### QueryProcessor
- Main entry point for retrieval operations
- Orchestrates the entire pipeline: query → embedding → search → reconstruction
- Handles metadata filtering and result formatting

### EmbeddingService
- Manages Cohere API calls for embedding generation
- Handles rate limiting and error recovery
- Caches embeddings for performance (optional)

### VectorSearchService
- Interfaces with Qdrant for similarity search
- Manages connection pooling and error handling
- Applies metadata filters during search

### ContextReconstructor
- Organizes retrieved chunks into coherent context
- Preserves section hierarchy and document order
- Formats results for downstream consumption

## Testing

### Run Unit Tests

```bash
# Run all retrieval unit tests
python -m pytest tests/unit/retrieval/ -v

# Run integration tests
python -m pytest tests/integration/ -v
```

### Performance Testing

```bash
# Test query performance
python -m pytest tests/performance/query_performance_test.py
```

## Troubleshooting

### Common Issues

1. **Connection Errors**:
   - Verify QDRANT_URL and QDRANT_API_KEY in your .env file
   - Check that the Qdrant collection exists and is accessible

2. **Cohere API Errors**:
   - Confirm COHERE_API_KEY is valid
   - Check API rate limits

3. **No Results Found**:
   - Verify the collection contains data from Spec-1
   - Check that query text is not empty or too short

### Performance Tips

- Monitor query response times using the verbose flag
- Adjust top_k parameter based on performance needs
- Consider implementing caching for frequently asked queries