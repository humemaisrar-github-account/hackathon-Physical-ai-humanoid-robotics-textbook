# Data Model: RAG Agent

**Feature**: 003-rag-agent
**Date**: 2025-12-29

## Core Entities

### QueryRequest
- **Description**: A request from the user containing a natural language question
- **Attributes**:
  - `query` (string): The user's natural language question
  - `top_k` (int): Number of results to retrieve (default: 5)
  - `include_sources` (bool): Whether to include source information in the response (default: true)

### QueryResponse
- **Description**: The structured response returned to the user
- **Attributes**:
  - `query` (string): The original user query
  - `answer` (string): The agent's response to the query
  - `sources` (list[SourceInfo]): List of sources used in the response
  - `retrieval_metadata` (RetrievalMetadata): Metadata about the retrieval process
  - `execution_time_ms` (float): Total time taken to process the query

### SourceInfo
- **Description**: Information about a source used in the response
- **Attributes**:
  - `source_url` (string): URL of the original document
  - `section_hierarchy` (list[string]): Hierarchical section information (e.g., ["Chapter 1", "Section 1.2"])
  - `chunk_id` (string): Unique identifier for the chunk
  - `similarity_score` (float): Similarity score of the chunk to the query

### RetrievalMetadata
- **Description**: Metadata about the retrieval process
- **Attributes**:
  - `retrieved_chunks_count` (int): Number of chunks retrieved
  - `top_k_used` (int): The top-K value used for retrieval
  - `retrieval_time_ms` (float): Time taken for retrieval process
  - `query_embedding_time_ms` (float): Time taken to generate query embedding
  - `search_time_ms` (float): Time taken for vector search

### AgentConfiguration
- **Description**: Configuration for the OpenAI agent
- **Attributes**:
  - `system_instructions` (string): Instructions for the agent's behavior
  - `model` (string): The OpenAI model to use
  - `temperature` (float): Temperature setting for response generation
  - `max_tokens` (int): Maximum tokens for response generation

### GroundingValidationResult
- **Description**: Result of the grounding validation process
- **Attributes**:
  - `is_valid` (bool): Whether the response is properly grounded
  - `citations_found` (bool): Whether sources were properly cited
  - `content_match_score` (float): How well the response matches retrieved content
  - `validation_details` (string): Details about the validation process

## API Schemas

### Request Schema (JSON)
```json
{
  "query": "natural language question text",
  "top_k": 5,
  "include_sources": true
}
```

### Response Schema (JSON)
```json
{
  "query": "natural language question text",
  "answer": "agent's response to the question",
  "sources": [
    {
      "source_url": "https://example.com/page",
      "section_hierarchy": ["Chapter 1", "Section 1.2"],
      "chunk_id": "chunk_001",
      "similarity_score": 0.85
    }
  ],
  "retrieval_metadata": {
    "retrieved_chunks_count": 3,
    "top_k_used": 5,
    "retrieval_time_ms": 120.5,
    "query_embedding_time_ms": 50.2,
    "search_time_ms": 70.3
  },
  "execution_time_ms": 850.2
}
```

## Data Flow

1. **Query Input**: User provides natural language question
2. **Retrieval**: Query is processed by the retrieval pipeline from Spec-2
3. **Context Assembly**: Retrieved chunks and metadata are assembled
4. **Agent Processing**: OpenAI agent processes query with retrieved context
5. **Grounding Validation**: Response is validated for grounding in retrieved content
6. **Response Formation**: QueryResponse object is created with all relevant information
7. **API Response**: Structured JSON response is returned to the user

## Integration with Existing Components

The RAG agent will integrate with the retrieval pipeline from Spec-2:
- Uses RetrievedChunk objects from the retrieval pipeline
- Passes retrieved context to the agent
- Maintains source information for citation in responses
- Reuses configuration and settings from existing components