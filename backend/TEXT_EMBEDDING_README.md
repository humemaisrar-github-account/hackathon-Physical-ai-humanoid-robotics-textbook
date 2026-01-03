# Text Embedding Service

This service provides comprehensive text embedding functionality using Cohere for embeddings and Qdrant for vector storage and retrieval.

## Features

- **Text to Embeddings Conversion**: Convert input text into high-dimensional embeddings using Cohere
- **Qdrant Integration**: Save embeddings into Qdrant collections with IDs and metadata
- **Similarity Search**: Retrieve relevant embeddings using vector similarity
- **Metadata Management**: Support for metadata filtering and management
- **Error Handling**: Comprehensive error handling and input validation
- **Logging**: Comprehensive logging for all operations
- **Health Checks**: Health check endpoints for monitoring
- **API Endpoints**: RESTful API for all operations

## Architecture

### Core Service: TextEmbeddingService

Located in `src/services/text_embedding_service.py`, this service provides:

- `convert_text_to_embeddings(texts: List[str])` - Convert multiple texts to embeddings
- `convert_single_text_to_embedding(text: str)` - Convert single text to embedding
- `save_embeddings_to_qdrant(texts, metadata_list=None, ids=None)` - Save embeddings to Qdrant
- `retrieve_similar_embeddings(query_text, top_k=5, filters=None)` - Retrieve similar embeddings
- `get_embedding_count()` - Get total count of embeddings
- `delete_embeddings_by_ids(ids)` - Delete embeddings by IDs

### API Endpoints: text_embedding.py

Located in `src/api/v1/text_embedding.py`, provides:

- `POST /api/v1/embed` - Convert texts to embeddings
- `POST /api/v1/save` - Save embeddings to Qdrant
- `POST /api/v1/search` - Search for similar embeddings
- `GET /api/v1/count` - Get embedding count
- `POST /api/v1/delete` - Delete embeddings by IDs
- `GET /api/v1/health` - Health check

## Configuration

The service uses the following environment variables from `.env`:

```
# Cohere API
COHERE_API_KEY="your-cohere-api-key"

# Qdrant Configuration
QDRANT_URL="your-qdrant-url"
QDRANT_API_KEY="your-qdrant-api-key"
QDRANT_COLLECTION_NAME="text_embeddings"  # Optional, defaults to "text_embeddings"
```

## Usage Examples

### Python Client

```python
from src.services.text_embedding_service import create_text_embedding_service

# Create the service
service = create_text_embedding_service()

# Convert texts to embeddings
texts = [
    "The future of artificial intelligence",
    "Machine learning algorithms"
]
embeddings = service.convert_text_to_embeddings(texts)

# Save embeddings to Qdrant with metadata
metadata = [
    {"category": "AI", "source": "example1", "topic": "future"},
    {"category": "ML", "source": "example2", "topic": "algorithms"}
]
saved_ids = service.save_embeddings_to_qdrant(texts, metadata)

# Retrieve similar embeddings
results = service.retrieve_similar_embeddings(
    query_text="artificial intelligence advancements",
    top_k=3
)

# Get total count
count = service.get_embedding_count()
```

### API Usage

```bash
# Convert texts to embeddings
curl -X POST http://localhost:8000/api/v1/embed \
  -H "Content-Type: application/json" \
  -d '{"texts": ["text1", "text2"]}'

# Save embeddings to Qdrant
curl -X POST http://localhost:8000/api/v1/save \
  -H "Content-Type: application/json" \
  -d '{"texts": ["text1"], "metadata_list": [{"category": "AI"}]}'

# Search for similar embeddings
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query_text": "artificial intelligence", "top_k": 5}'
```

## Error Handling and Validation

- Input validation with clear error messages
- Reasonable limits (max 100 texts per request)
- Proper HTTP status codes (400 for bad requests, 500 for server errors)
- Comprehensive error logging
- Graceful handling of service unavailability

## Metadata Management

- Automatic metadata generation (created_at timestamps, IDs)
- Support for custom metadata fields
- Preservation of original text in payload
- Filtering support in similarity search

## Testing

### Unit Tests

Run the embedding functionality test:
```bash
python test_embeddings_only.py
```

This tests the core embedding functionality without requiring Qdrant.

### Full Integration Tests

Run the complete test suite:
```bash
python text_embedding_demo.py
```

Note: This requires a working Qdrant instance.

## Production Deployment

1. Set up environment variables with API keys
2. Ensure Qdrant is accessible and properly configured
3. Deploy the FastAPI application
4. Set up monitoring and logging
5. Implement API authentication as needed

## Security Considerations

- API key validation for protected endpoints
- Input sanitization and validation
- Rate limiting (to be implemented)
- Secure transport (HTTPS in production)

## Performance Considerations

- Batch processing for multiple embeddings
- Efficient vector search in Qdrant
- Connection pooling for external services
- Caching for frequently accessed embeddings (optional enhancement)

## Monitoring

- Comprehensive logging for all operations
- Health check endpoints
- Performance metrics (to be enhanced)
- Error tracking and alerting