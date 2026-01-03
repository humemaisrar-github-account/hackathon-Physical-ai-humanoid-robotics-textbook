# Research: Integrated RAG Chatbot for AI-Native Textbook

**Feature**: 001-rag-chatbot-integration
**Date**: 2025-12-28
**Research completed for**: Implementation planning phase

## Research Findings Summary

This document captures research findings for key technical decisions in the RAG chatbot implementation, addressing the critical questions raised in the feature requirements.

## Decision: Embedding Model Selection

**Rationale**: For free-tier constraints and textbook content retrieval, OpenAI's text-embedding-3-small model offers the best balance of accuracy, cost, and performance. It provides high-quality embeddings while being cost-effective for the free-tier environment.

**Alternatives considered**:
- Sentence Transformers (all-MiniLM-L6-v2): Self-hosted option but requires more computational resources
- Cohere embeddings: Good quality but adds another API dependency
- text-embedding-ada-002: More expensive than text-embedding-3-small

## Decision: Chunking Methodology

**Rationale**: Semantic chunking using sentence boundary detection provides better retrieval quality for textbook content compared to fixed-length chunks. This approach maintains context coherence while optimizing for the RAG system's retrieval effectiveness.

**Alternatives considered**:
- Fixed-length chunking (512 tokens): Simpler but may break semantic boundaries
- Recursive splitting: Could work but semantic chunking better preserves textbook structure
- Document-section based: Good for textbooks but requires document structure parsing

## Decision: Agent Orchestration Layer

**Rationale**: OpenAI Assistants API provides better tool integration and state management for complex RAG workflows compared to raw ChatCompletions. It handles conversation threading and tool calling more elegantly for the multi-step RAG process.

**Alternatives considered**:
- Raw ChatCompletions API: More control but requires manual state management
- LangChain agents: Heavy dependency, may exceed free-tier constraints
- CrewAI: Good for multi-agent systems but overkill for this use case

## Decision: Qdrant Collection Structure

**Rationale**: Single collection with metadata filtering provides optimal performance for textbook retrieval. Payload schema includes content, chapter reference, section, and embedding vectors with indexed metadata for efficient filtering.

**Schema design**:
- `content`: Text content of the chunk
- `chapter_id`: Reference to textbook chapter
- `section`: Section within the chapter
- `metadata`: Additional context information
- `vector`: Embedding vector

## Decision: BetterAuth Session Handling

**Rationale**: Database sessions with JWT tokens provide secure authentication while maintaining user state across requests. Background metadata stored as JSON in user profile allows for personalization features.

**Implementation approach**:
- Database adapter for Neon Postgres
- JWT for session management
- Custom user model extending BetterAuth with background fields

## Decision: Chapter Personalization Approach

**Rationale**: Hybrid approach combining content rewriting with layered summaries provides the best balance of personalization effectiveness and computational efficiency. Full rewrite preserves formatting while layered approach allows for targeted adjustments.

**Approach**:
- Use LLM to generate personalized versions based on user background
- Preserve original formatting through structured output
- Cache personalized versions to reduce computation

## Decision: Urdu Translation Strategy

**Rationale**: Direct translation with terminology refinement ensures technical accuracy while maintaining readability. Using specialized prompting for technical terms improves translation quality for AI/CS content.

**Approach**:
- Multi-step translation process with technical term identification
- Preservation of code blocks and formatting
- Quality validation against original meaning

## Decision: Deployment Platform

**Rationale**: Railway or Vercel provide suitable free-tier options for the backend and frontend respectively, with good integration and minimal cold-start issues. Both support the required technologies and have educational discounts.

**Alternatives considered**:
- Heroku: Good but has more restrictions on free tier
- Render: Alternative option but Railway has better Python support
- AWS/GCP: Overkill for free-tier requirements

## Additional Research: Docusaurus Integration

**Method**: Using Docusaurus' plugin system to inject the chatbot component into textbook pages. Custom React component that can be embedded via MDX or injected via plugin.

**Approach**:
- Docusaurus plugin for chatbot integration
- Event listeners for text selection
- Responsive design that doesn't disrupt reading flow

## Additional Research: Retrieval Strategies

**Method**: Hybrid search combining semantic search in Qdrant with optional keyword matching for improved recall. Re-ranking approach to improve precision.

**Approach**:
- Primary: Semantic search using vector similarity
- Secondary: Keyword-based fallback
- Re-ranking using cross-encoder for top candidates