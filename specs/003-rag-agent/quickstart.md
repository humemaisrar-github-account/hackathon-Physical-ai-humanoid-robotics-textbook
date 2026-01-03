# Quickstart: RAG Agent

**Feature**: 003-rag-agent
**Date**: 2025-12-29

## Prerequisites

- Python 3.11 or higher
- UV package manager
- OpenAI API key
- Qdrant Cloud account and collection (from Spec-1)
- Cohere API key (for retrieval pipeline from Spec-2)
- Access to the vector collection created in Spec-1
- Access to the retrieval pipeline from Spec-2

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
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Qdrant Configuration
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=your_collection_name_from_spec1

# Cohere Configuration
COHERE_API_KEY=your_cohere_api_key
COHERE_MODEL_NAME=embed-multilingual-v2.0  # Or the model used in Spec-1

# Application Configuration
TOP_K_DEFAULT=5
DEBUG=false
</env>

### 3. Verify Dependencies

Test that all required services are accessible:

```bash
# Test OpenAI connection
python -c "import openai; print('OpenAI connection successful')" 2>/dev/null || echo "OpenAI import failed"

# Test Qdrant and Cohere connections (from Spec-2 retrieval pipeline)
python -c "from src.retrieval.query_processor import QueryProcessor; print('Retrieval pipeline accessible')"
```

## Usage Examples

### 1. Starting the FastAPI Server

```bash
# Start the RAG agent server
uvicorn src.api.rag_agent_endpoints:app --host 0.0.0.0 --port 8000 --reload

# The server will be available at http://localhost:8000
```

### 2. Making API Requests

```bash
# Basic query request
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key concepts in machine learning?",
    "top_k": 5,
    "include_sources": true
  }'
```

### 3. Python Client Example

```python
import requests

# Configure the API endpoint
BASE_URL = "http://localhost:8000"

# Make a query request
response = requests.post(
    f"{BASE_URL}/query",
    json={
        "query": "Explain neural networks",
        "top_k": 3,
        "include_sources": True
    }
)

# Process the response
data = response.json()
print(f"Answer: {data['answer']}")
print(f"Sources: {len(data['sources'])} sources used")
for source in data['sources']:
    print(f"- {source['source_url']}")
```

## Key Components

### AgentService
- Main integration point with OpenAI Agent SDK
- Handles agent creation and configuration
- Processes queries with retrieved context
- Ensures grounding validation

### QueryHandler
- Orchestrates the complete flow: query → retrieval → agent → response
- Manages the interaction between retrieval pipeline and agent
- Formats responses according to specifications

### GroundingValidator
- Validates that agent responses are grounded in retrieved content
- Checks for proper source citation
- Prevents hallucination and ensures accuracy

### API Endpoints
- FastAPI endpoints for the RAG agent
- Request/response schema validation
- Error handling and logging

## Testing

### Run Unit Tests

```bash
# Run all RAG agent unit tests
python -m pytest tests/unit/rag_agent/ -v

# Run API tests
python -m pytest tests/unit/api/ -v

# Run integration tests
python -m pytest tests/integration/ -v
```

### Performance Testing

```bash
# Test query performance
python -m pytest tests/performance/rag_agent_performance_test.py
```

## Configuration Options

### Agent Configuration
- **System Instructions**: Define behavior (grounded responses, source citation)
- **Model Selection**: Choose appropriate OpenAI model
- **Temperature**: Control response randomness
- **Max Tokens**: Limit response length

### Retrieval Configuration
- **Top-K**: Number of chunks to retrieve (default: 5)
- **Include Sources**: Whether to include source information (default: true)
- **Similarity Threshold**: Minimum similarity for chunk inclusion

## Troubleshooting

### Common Issues

1. **OpenAI API Errors**:
   - Verify OPENAI_API_KEY is valid
   - Check API rate limits

2. **Qdrant Connection Errors**:
   - Verify QDRANT_URL and QDRANT_API_KEY in your .env file
   - Check that the Qdrant collection exists and is accessible

3. **Cohere API Errors**:
   - Confirm COHERE_API_KEY is valid
   - Check API rate limits

4. **No Results Found**:
   - Verify the collection contains data from Spec-1
   - Check that query text is not empty or too short

### Performance Tips

- Monitor query response times using the execution_time_ms field
- Adjust top_k parameter based on performance needs
- Consider implementing caching for frequently asked queries
- Use appropriate OpenAI models for performance vs. quality trade-offs