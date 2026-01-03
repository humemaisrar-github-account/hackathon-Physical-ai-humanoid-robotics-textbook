# Data Model: Retrieval Pipeline

**Feature**: 002-retrieval-pipeline
**Date**: 2025-12-29

## Core Entities

### Query
- **Description**: A natural language search request from the user
- **Attributes**:
  - `text` (string): The original query text
  - `embedding` (list[float]): Vector representation of the query
  - `filters` (dict): Optional metadata filters to apply
  - `top_k` (int): Number of results to retrieve (default: 5)

### RetrievedChunk
- **Description**: A content segment returned by the retrieval system
- **Attributes**:
  - `id` (string): Unique identifier for the chunk
  - `text` (string): Original text content of the chunk
  - `score` (float): Similarity score relative to the query
  - `source_url` (string): URL of the original document
  - `section_hierarchy` (list[string]): Hierarchical section information (e.g., ["Chapter 1", "Section 1.2", "Subsection 1.2.1"])
  - `chunk_metadata` (dict): Additional metadata stored with the vector
  - `position` (int): Position of the chunk in the original document

### SearchResult
- **Description**: Collection of retrieved chunks for a single query
- **Attributes**:
  - `query` (Query): The original query that generated these results
  - `chunks` (list[RetrievedChunk]): List of relevant content chunks
  - `execution_time` (float): Time taken to execute the search (ms)
  - `query_embedding_time` (float): Time taken to generate query embedding (ms)
  - `search_time` (float): Time taken for vector search (ms)

### MetadataFilter
- **Description**: Criteria used to filter search results by metadata
- **Attributes**:
  - `field` (string): The metadata field to filter on (e.g., "source_url", "section")
  - `operator` (string): The comparison operator (e.g., "equals", "contains", "in")
  - `value` (any): The value to compare against

## Qdrant Collection Schema

### Vector Collection: `book_content_chunks`
- **Vector Dimensions**: Same as used in Spec-1 (determined by Cohere model)
- **Distance Metric**: Cosine similarity
- **Payload Structure**:
  ```json
  {
    "text": "string",
    "source_url": "string",
    "section_hierarchy": ["string"],
    "chunk_id": "string",
    "position": "integer"
  }
  ```

## Data Flow

1. **Query Input**: User provides natural language query
2. **Embedding Generation**: Query is converted to vector using Cohere
3. **Vector Search**: Qdrant performs similarity search using cosine distance
4. **Result Assembly**: Retrieved vectors are converted back to RetrievedChunk objects with metadata
5. **Context Reconstruction**: Chunks are organized and prepared for downstream use
6. **Response Formation**: SearchResult object is created with all relevant information

## Serialization Format

### Input Query (JSON)
```json
{
  "query": "natural language query text",
  "top_k": 5,
  "filters": {
    "source_url": "https://example.com/page",
    "section": "Chapter 1"
  }
}
```

### Output Results (JSON)
```json
{
  "query": "natural language query text",
  "results": [
    {
      "id": "chunk_id",
      "text": "retrieved text content",
      "score": 0.85,
      "source_url": "https://example.com/page",
      "section_hierarchy": ["Chapter 1", "Section 1.2"],
      "position": 1
    }
  ],
  "execution_time_ms": 120.5,
  "retrieval_count": 3
}
```