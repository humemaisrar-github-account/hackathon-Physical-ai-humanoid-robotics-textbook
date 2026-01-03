# Text Embedding Service Implementation

This project provides a complete implementation for converting text to embeddings, saving them to Qdrant, and retrieving relevant data based on similarity search.

## Features

1. **Text to Embedding Conversion** - Uses Cohere's API to convert text to high-dimensional embeddings
2. **Qdrant Integration** - Stores embeddings with appropriate IDs and metadata
3. **Similarity Search** - Retrieves the most relevant embeddings based on similarity
4. **REST API Endpoints** - Provides HTTP endpoints for all operations
5. **Error Handling** - Comprehensive error handling and validation

## Architecture

### Core Components

- `TextEmbeddingService` - Main service class handling all embedding operations
- `text_embedding.py` - API endpoints for embedding operations
- `settings.py` - Configuration management

### Service Methods

1. `convert_text_to_embeddings(texts: List[str])` - Convert multiple texts to embeddings
2. `convert_single_text_to_embedding(text: str)` - Convert single text to embedding
3. `save_embeddings_to_qdrant(texts, metadata_list=None, ids=None)` - Save embeddings to Qdrant
4. `retrieve_similar_embeddings(query_text, top_k=5)` - Retrieve similar embeddings
5. `get_embedding_count()` - Get total count of embeddings in collection
6. `delete_embeddings_by_ids(ids)` - Delete embeddings by IDs

## API Endpoints

### `/api/v1/embed` (POST)
Convert texts to embeddings
```json
{
  "texts": ["text1", "text2", "text3"]
}
```

### `/api/v1/save` (POST)
Save embeddings to Qdrant
```json
{
  "texts": ["text1", "text2"],
  "metadata_list": [
    {"category": "AI", "source": "example"},
    {"category": "ML", "source": "example"}
  ]
}
```

### `/api/v1/search` (POST)
Search for similar embeddings
```json
{
  "query_text": "artificial intelligence",
  "top_k": 5
}
```

### `/api/v1/count` (GET)
Get embedding count

### `/api/v1/delete` (POST)
Delete embeddings by IDs
```json
{
  "ids": ["id1", "id2"]
}
```

## Usage Examples

### Python Client Usage

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
print(f"Generated {len(embeddings)} embeddings")

# Save embeddings to Qdrant
metadata = [
    {"category": "AI", "source": "example1"},
    {"category": "ML", "source": "example2"}
]
saved_ids = service.save_embeddings_to_qdrant(texts, metadata)
print(f"Saved with IDs: {saved_ids}")

# Retrieve similar embeddings
results = service.retrieve_similar_embeddings(
    query_text="artificial intelligence advancements",
    top_k=3
)
for result in results:
    print(f"ID: {result['id']}, Score: {result['score']}, Text: {result['text']}")
```

### Direct API Usage

```bash
# Embed texts
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

## Configuration

The service uses the following environment variables (defined in `.env`):

```
# Cohere API
COHERE_API_KEY="your-cohere-api-key"

# Qdrant Cloud
QDRANT_URL="your-qdrant-url"
QDRANT_API_KEY="your-qdrant-api-key"

# Collection name (optional)
QDRANT_COLLECTION_NAME="text_embeddings"
```

## Running the Service

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`

3. Start the API server:
```bash
cd backend
python -m src.main
```

4. The API will be available at `http://localhost:8000`

## Testing

Run the functionality test:
```bash
cd backend
python test_embeddings_only.py
```

This tests the core embedding functionality without requiring a Qdrant instance.

## Implementation Details

- **Embedding Model**: Uses Cohere's `embed-english-v3.0` model
- **Vector Size**: 1024-dimensional embeddings
- **Distance Metric**: Cosine similarity in Qdrant
- **Metadata Storage**: Each embedding includes original text and custom metadata
- **Error Handling**: Comprehensive error handling with appropriate HTTP status codes
- **Logging**: Detailed logging for debugging and monitoring