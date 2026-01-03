# Spec-4 Plan: Frontend–Backend Integration & In-Book RAG Chatbot UI

## 1. Scope and Dependencies

### In Scope
- Create FastAPI endpoint for chat interactions with RAG agent
- Implement natural language question processing
- Develop grounded responses with source citations
- Support "selected text only" mode
- Handle loading, error, and empty-response states
- Ensure compatibility with Docusaurus frontend integration
- Maintain existing functionality while adding new features

### Out of Scope
- Frontend UI implementation (to be handled separately by frontend team)
- Database schema changes beyond existing Qdrant integration
- Authentication system modifications
- External API key management beyond existing setup

### External Dependencies
- FastAPI framework for backend endpoints
- Qdrant vector database for document retrieval
- Cohere embedding model for text embeddings
- Existing embedding and retrieval services
- Docusaurus framework for frontend integration

## 2. Key Decisions and Rationale

### API Design Decision
**Options Considered:**
- RESTful API vs GraphQL
- Streaming vs Non-streaming responses
- Direct database access vs Service layer pattern

**Decision:** RESTful API with non-streaming responses using service layer pattern
**Rationale:** Simpler to implement and integrate with Docusaurus frontend, consistent with existing API patterns

### Error Handling Strategy
**Options Considered:**
- Custom exception handlers vs Standard HTTP exceptions
- Detailed error messages vs Generic messages
- Logging levels and strategies

**Decision:** Standard HTTP exceptions with structured error responses and comprehensive logging
**Rationale:** Consistent with existing FastAPI patterns and provides sufficient debugging information

### Service Architecture
**Options Considered:**
- Global service instances vs Dependency injection
- Monolithic vs Modular service structure
- Synchronous vs Asynchronous processing

**Decision:** Dependency injection with asynchronous processing
**Rationale:** Better testability, avoids circular imports, follows FastAPI best practices

## 3. Interfaces and API Contracts

### Public APIs
**Input:** POST `/api/v1/chat`
```json
{
  "query": "string (required)",
  "selected_text": "string (optional)",
  "top_k": "integer (optional, default: 3)",
  "include_sources": "boolean (optional, default: true)"
}
```

**Output:** 200 OK
```json
{
  "response": "string",
  "sources": [{"content": "string", "metadata": "object", "url": "string", "title": "string"}],
  "query_id": "string",
  "timing": {"retrieval_time": "float", "agent_time": "float", "total_time": "float"}
}
```

**Errors:**
- 400: Invalid query or parameters
- 401: Invalid API key
- 500: Internal server error

### Versioning Strategy
- API versioning through URL path (`/api/v1/`)
- Backward compatible changes within same version
- New endpoints for breaking changes

### Error Taxonomy
- INVALID_QUERY (400): Malformed or empty query
- INVALID_TOP_K (400): Invalid top_k parameter
- AUTH_ERROR (401): Invalid API key
- INTERNAL_ERROR (500): Server-side issues

## 4. Non-Functional Requirements (NFRs) and Budgets

### Performance
- p95 latency: < 2 seconds for typical queries
- Throughput: Handle 10 concurrent users
- Resource caps: Memory usage < 512MB during processing

### Reliability
- SLOs: 99% uptime for chat endpoint
- Error budget: 1% for chat functionality
- Degradation strategy: Fallback to mock service when external dependencies unavailable

### Security
- AuthN/AuthZ: API key validation for all requests
- Data handling: No sensitive data stored in responses
- Secrets: API keys managed through environment variables
- Auditing: All queries logged for monitoring

### Cost
- Unit economics: Designed to minimize API calls to external services
- Resource efficiency: Reuse existing embedding and retrieval services

## 5. Data Management and Migration

### Source of Truth
- Document embeddings stored in Qdrant collection
- Real-time retrieval from existing indexed content
- No persistent storage of chat history

### Schema Evolution
- Flexible metadata handling for source citations
- Extensible response format for future enhancements

### Migration Strategy
- No database migration required (uses existing Qdrant collection)
- Zero-downtime deployment possible

## 6. Operational Readiness

### Observability
- Structured logging for all operations
- Performance timing for retrieval and agent processing
- Error logging with stack traces

### Alerting
- Thresholds for response times > 5 seconds
- Error rate monitoring (> 5% error rate triggers alert)

### Runbooks
- Common error troubleshooting procedures
- Service restart procedures
- API key rotation process

### Deployment and Rollback
- Standard FastAPI deployment process
- Environment-specific configuration
- Quick rollback capability through version control

## 7. Risk Analysis and Mitigation

### Top 3 Risks
1. **External API Availability** - Risk of external agent service being unavailable
   - Mitigation: Mock service fallback for testing and degraded operation

2. **Performance Degradation** - Long response times affecting user experience
   - Mitigation: Timeout handling and performance monitoring

3. **Data Quality Issues** - Poor embeddings affecting response quality
   - Mitigation: Input validation and quality checks on retrieved documents

### Blast Radius
- Limited to chat functionality; existing endpoints unaffected
- Isolated service with minimal dependencies on other components

### Kill Switches/Guardrails
- API key validation acts as circuit breaker
- Parameter validation prevents invalid requests
- Resource limits prevent excessive processing

## 8. Evaluation and Validation

### Definition of Done
- [x] Chat endpoint implemented and registered
- [x] Natural language processing working
- [x] Source citations included in responses
- [x] Selected text mode supported
- [x] Error handling implemented
- [x] Performance timing included
- [x] Mock service for testing without API keys
- [x] Proper logging implemented
- [x] All existing functionality preserved

### Output Validation
- [x] Response format matches specification
- [x] Source citations contain required metadata
- [x] Error responses follow standard format
- [x] Performance metrics are accurate
- [x] Input validation prevents malformed requests