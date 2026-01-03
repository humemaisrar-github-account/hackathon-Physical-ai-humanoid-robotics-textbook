---
id: 003
title: RAG Chatbot Plan
stage: plan
date: 2025-12-28
surface: agent
model: claude-sonnet-4-5-20250929
feature: rag-chatbot-integration
branch: 001-rag-chatbot-integration
user: user
command: sp.plan
labels: [planning, architecture, rag, chatbot]
links:
  spec: specs/001-rag-chatbot-integration/spec.md
  plan: specs/001-rag-chatbot-integration/plan.md
  research: specs/001-rag-chatbot-integration/research.md
  data-model: specs/001-rag-chatbot-integration/data-model.md
  quickstart: specs/001-rag-chatbot-integration/quickstart.md
  adr: null
  pr: null
files:
 - specs/001-rag-chatbot-integration/plan.md
 - specs/001-rag-chatbot-integration/research.md
 - specs/001-rag-chatbot-integration/data-model.md
 - specs/001-rag-chatbot-integration/quickstart.md
 - specs/001-rag-chatbot-integration/contracts/rag-api.yaml
tests:
 - none
---

## Prompt

Integrated RAG Chatbot for AI-Native Textbook

Create:
- Architecture sketch covering:
  - Frontend integration within the Docusaurus environment
  - Backend services implemented using FastAPI
  - Retrieval workflow powered by Qdrant vector database
  - Neon Postgres data schema for authentication, user background, and personalization state
  - OpenAI Agents / ChatKit orchestration and tool execution flow
  - Optional architecture for Claude Code Subagents and reusable Agent Skills
- Section structure for development phases:
  1. Core RAG chatbot implementation
  2. Selected-text-only question answering capability
  3. Bonus features (Reusable Intelligence, BetterAuth authentication, personalization, Urdu translation)
- Research approach for:
  - Analyzing and selecting optimal retrieval strategies for textbook content
  - Designing an effective and non-disruptive user experience inside Docusaurus
  - Choosing appropriate embedding models, chunking strategies, and context window sizes
- Quality validation criteria aligned with hackathon evaluation:
  - Retrieval precision and relevance
  - UI robustness and stability
  - Authentication reliability
  - Accuracy of personalized and translated chapter outputs

Decisions needing documentation:
- Embedding model selection (balancing accuracy, latency, and free-tier constraints)
- Chunking methodology (semantic chunking vs. fixed-length chunks)
- Choice between Agents or ChatKit as the primary orchestration layer
- Qdrant collection structure and payload schema design
- BetterAuth session handling strategy and background-metadata representation
- Chapter personalization approach (full rewrite vs. layered summary vs. hybrid strategy)
- Urdu translation fidelity strategy (direct translation vs. translation with terminology refinement)
- Deployment platform choice (free-tier limitations and cold-start considerations)

Testing strategy:
- Unit tests for:
  - Text chunking logic
  - Embedding generation pipeline
  - Retrieval accuracy against predefined queries
- Integration tests for:
  - End-to-end FastAPI, Qdrant, and Neon interaction
  - Authenticated versus unauthenticated user flows
- Functional tests:
  - Correctness of book-wide question answering
  - Correctness of selected-text-only question answering
  - Validation of personalized chapter outputs
  - Accuracy and formatting preservation in Urdu translations
- Acceptance validation:
  - Verification against the 100-point base score and bonus feature scoring rubrics

Technical details:
- Adopt an iterative, research-driven development approach:
  - Explore retrieval strategies and agent tooling in parallel with implementation
  - Refine components based on continuous validation feedback
- Maintain a modular codebase structure:
  - `agents/`, `skills/`, `api/`, `db/`, `ui/`, `personalization/`, `translation/`
- Adhere strictly to specification constraints:
  - OpenAI Agents/ChatKit with FastAPI, Qdrant Cloud Free Tier, and Neon Postgres
  - Docusaurus as the exclusive frontend framework
- Organize work by phase

## Response snapshot

# Implementation Plan: Integrated RAG Chatbot for AI-Native Textbook

**Branch**: `001-rag-chatbot-integration` | **Date**: 2025-12-28 | **Spec**: [specs/001-rag-chatbot-integration/spec.md](specs/001-rag-chatbot-integration/spec.md)
**Input**: Feature specification from `/specs/001-rag-chatbot-integration/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of an embedded RAG chatbot for Docusaurus-based AI-native textbook with dual-mode question answering (book-wide and selected-text-only). The system will use OpenAI Agents/ChatKit for orchestration, FastAPI backend, Qdrant vector database for retrieval, and Neon Postgres for authentication and user data. The architecture will support core RAG functionality, authentication with BetterAuth, chapter personalization, and Urdu translation as bonus features.

## Technical Context

**Language/Version**: Python 3.11, JavaScript/TypeScript for frontend integration
**Primary Dependencies**: FastAPI, OpenAI Agents/ChatKit, Qdrant, Neon Postgres, BetterAuth, Docusaurus
**Storage**: Neon Serverless Postgres (user data), Qdrant Cloud (vector embeddings), filesystem (optional caching)
**Testing**: pytest, integration tests for API contracts, end-to-end tests for user flows
**Target Platform**: Web application (Docusaurus frontend + FastAPI backend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: <10s response time for 95th percentile, support 100+ concurrent users
**Constraints**: Free-tier limitations for Qdrant and Neon, must preserve textbook reading flow
**Scale/Scope**: Single textbook corpus with multiple users, personalization based on user profiles

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Reliability & Accuracy**: RAG responses must be grounded in textbook content with no hallucinations
- **Production-Oriented Engineering**: Follow industry-grade patterns for RAG pipelines, API design, and data storage
- **Modular & Future-Ready Design**: Components must be loosely coupled to enable future enhancements
- **Data Security & Privacy**: User background data must be handled securely with proper privacy compliance
- **Context-Aware User Experience**: Chatbot responses must align with chapter context and selected text
- **Implementation Standards for RAG**: Use OpenAI Agents/ChatKit, FastAPI, Neon Postgres, Qdrant Cloud
- **Textbook Integration Requirements**: Chatbot must embed directly in Docusaurus with theme alignment

## Project Structure

### Documentation (this feature)
```text
specs/001-rag-chatbot-integration/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)
```text
backend/
├── src/
│   ├── agents/
│   │   ├── rag_agent.py
│   │   ├── personalization_agent.py
│   │   └── translation_agent.py
│   ├── skills/
│   │   ├── retrieval_skill.py
│   │   ├── content_extraction_skill.py
│   │   └── summarization_skill.py
│   ├── api/
│   │   ├── rag_routes.py
│   │   ├── auth_routes.py
│   │   └── personalization_routes.py
│   ├── models/
│   │   ├── user.py
│   │   ├── textbook_content.py
│   │   └── chat_session.py
│   ├── services/
│   │   ├── rag_service.py
│   │   ├── auth_service.py
│   │   ├── personalization_service.py
│   │   └── translation_service.py
│   └── db/
│       ├── connection.py
│       └── schema.py
└── tests/
    ├── unit/
    ├── integration/
    └── contract/

frontend/
├── src/
│   ├── components/
│   │   ├── RagChatbot.jsx
│   │   ├── ChatInterface.jsx
│   │   └── PersonalizationPanel.jsx
│   ├── pages/
│   │   └── TextbookPage.jsx
│   └── services/
│       ├── api_client.js
│       └── text_selection.js
└── tests/
    ├── unit/
    └── integration/
```

**Structure Decision**: Web application structure selected with separate backend and frontend directories to support FastAPI backend services and Docusaurus frontend integration. Backend contains agents, skills, API routes, models, and services. Frontend contains React components for chatbot interface and integration with Docusaurus.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

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

# Data Model: Integrated RAG Chatbot for AI-Native Textbook

**Feature**: 001-rag-chatbot-integration
**Date**: 2025-12-28

## Entity: User
**Description**: Represents a textbook reader with authentication status, software background, and hardware background information

**Fields**:
- `id` (UUID): Unique identifier for the user
- `email` (String): User's email address for authentication
- `name` (String): User's full name
- `software_background` (JSON): User's software development background and experience
- `hardware_background` (JSON): User's hardware experience and knowledge
- `created_at` (DateTime): Timestamp when user account was created
- `updated_at` (DateTime): Timestamp when user account was last updated
- `is_authenticated` (Boolean): Authentication status of the user

**Validation Rules**:
- Email must be unique and valid
- Name must be provided
- Background fields must be valid JSON structure
- Created timestamp is auto-generated

## Entity: TextbookContent
**Description**: Represents the educational material that serves as the knowledge base for RAG operations

**Fields**:
- `id` (UUID): Unique identifier for the content chunk
- `chapter_id` (String): Reference to the textbook chapter
- `section_title` (String): Title of the section within the chapter
- `content` (Text): The actual text content
- `embedding_vector` (Vector): Vector representation for similarity search
- `page_reference` (String): Original page number or location reference
- `metadata` (JSON): Additional metadata like difficulty level, concepts covered
- `created_at` (DateTime): Timestamp when content was indexed

**Validation Rules**:
- Content must be non-empty
- Chapter ID must reference valid chapter
- Embedding vector must be properly formatted
- Metadata must be valid JSON

## Entity: ChatSession
**Description**: Represents an interaction context between user and the RAG system

**Fields**:
- `id` (UUID): Unique identifier for the chat session
- `user_id` (UUID): Reference to the user (nullable for anonymous sessions)
- `session_token` (String): Unique token for session identification
- `mode` (String): Question answering mode (book-wide, selected-text-only)
- `created_at` (DateTime): Timestamp when session started
- `updated_at` (DateTime): Timestamp of last activity
- `is_active` (Boolean): Whether session is currently active

**Validation Rules**:
- Mode must be one of allowed values
- User ID must reference valid user if provided
- Session token must be unique

## Entity: ChatMessage
**Description**: Represents individual messages within a chat session

**Fields**:
- `id` (UUID): Unique identifier for the message
- `session_id` (UUID): Reference to the chat session
- `user_id` (UUID): Reference to the user who sent the message
- `message_type` (String): Type of message (user_query, system_response)
- `content` (Text): The actual message content
- `retrieved_context` (JSON): Context retrieved for system responses
- `created_at` (DateTime): Timestamp when message was created

**Validation Rules**:
- Session ID must reference valid session
- Message type must be one of allowed values
- Content must be non-empty

## Entity: RetrievedContext
**Description**: Represents the textbook passages retrieved by the vector search system for answer generation

**Fields**:
- `id` (UUID): Unique identifier for the retrieved context
- `session_id` (UUID): Reference to the chat session
- `query` (Text): The original user query
- `retrieved_chunks` (JSON): List of content chunks retrieved
- `relevance_scores` (JSON): Relevance scores for each chunk
- `created_at` (DateTime): Timestamp when retrieval was performed

**Validation Rules**:
- Session ID must reference valid session
- Retrieved chunks must be valid content references
- Relevance scores must be numeric values

## Entity: PersonalizationProfile
**Description**: Represents user-specific customizations applied to textbook content

**Fields**:
- `id` (UUID): Unique identifier for the profile
- `user_id` (UUID): Reference to the user
- `chapter_id` (String): Reference to the textbook chapter
- `personalization_settings` (JSON): User preferences for content adaptation
- `generated_content` (Text): Personalized version of the chapter
- `last_updated` (DateTime): Timestamp of last personalization update
- `formatting_preserved` (Boolean): Whether original formatting was maintained

**Validation Rules**:
- User ID must reference valid user
- Chapter ID must be valid
- Personalization settings must be valid JSON

## Entity: TranslationCache
**Description**: Represents cached Urdu translations of textbook chapters

**Fields**:
- `id` (UUID): Unique identifier for the translation
- `chapter_id` (String): Reference to the original textbook chapter
- `original_content_hash` (String): Hash of original content for cache validation
- `urdu_translation` (Text): Translated content in Urdu
- `translation_metadata` (JSON): Information about translation quality and confidence
- `created_at` (DateTime): Timestamp when translation was cached
- `expires_at` (DateTime): Timestamp when cache entry expires

**Validation Rules**:
- Chapter ID must be valid
- Content hash must match original
- Translation must be in valid Urdu text

## Entity: UserBackground
**Description**: Additional entity to store user background information separately

**Fields**:
- `id` (UUID): Unique identifier
- `user_id` (UUID): Reference to the user
- `background_type` (String): Type of background (software, hardware)
- `experience_level` (String): Experience level (beginner, intermediate, expert)
- `domains` (JSON): Specific domains of expertise
- `preferences` (JSON): Learning preferences and interests
- `created_at` (DateTime): Timestamp when background was captured

**Validation Rules**:
- User ID must reference valid user
- Background type must be one of allowed values
- Experience level must be one of allowed values

## Relationships

- **User** (1) ←→ (Many) **ChatSession**: Users can have multiple chat sessions
- **ChatSession** (1) ←→ (Many) **ChatMessage**: Each session contains multiple messages
- **ChatSession** (1) ←→ (Many) **RetrievedContext**: Each session has multiple retrieval operations
- **User** (1) ←→ (Many) **PersonalizationProfile**: Users can have multiple personalized chapters
- **User** (1) ←→ (Many) **UserBackground**: Users can have multiple background records (software/hardware)
- **TextbookContent** (1) ←→ (Many) **RetrievedContext**: Content can be retrieved in multiple contexts

# Quickstart Guide: Integrated RAG Chatbot for AI-Native Textbook

**Feature**: 001-rag-chatbot-integration
**Date**: 2025-12-28

## Overview
This guide provides step-by-step instructions to set up and run the Integrated RAG Chatbot for AI-Native Textbook project.

## Prerequisites
- Python 3.11+
- Node.js 18+ (for Docusaurus frontend)
- Access to OpenAI API (for agents and embeddings)
- Access to Qdrant Cloud (Free Tier)
- Access to Neon Serverless Postgres
- Git

## Setup Instructions

### 1. Clone and Initialize the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables by creating a `.env` file:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   QDRANT_URL=your_qdrant_cluster_url
   QDRANT_API_KEY=your_qdrant_api_key
   DATABASE_URL=your_neon_postgres_connection_string
   BETTER_AUTH_SECRET=your_auth_secret
   GEMINI_API_KEY=your_gemini_api_key  # If using Gemini
   ```

### 3. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables in `.env`:
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api
   ```

### 4. Database Setup
1. Run database migrations:
   ```bash
   cd backend
   python -m src.db.migrate
   ```

### 5. Index Textbook Content
1. Prepare your textbook content in the required format
2. Run the indexing script:
   ```bash
   python -m src.services.content_indexer --source path/to/textbook
   ```

### 6. Run the Applications

#### Backend (FastAPI)
1. From the backend directory:
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   ```

#### Frontend (Docusaurus)
1. From the frontend directory:
   ```bash
   npm start
   ```

## API Endpoints
- `GET /api/health` - Health check
- `POST /api/rag/chat` - RAG chat interaction
- `POST /api/rag/query` - Query with selected text context
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/personalization/chapter/{chapter_id}` - Get personalized chapter
- `POST /api/translation/urdu` - Get Urdu translation

## Testing
1. Run unit tests:
   ```bash
   # Backend
   cd backend
   pytest tests/unit/

   # Frontend
   cd frontend
   npm test
   ```

2. Run integration tests:
   ```bash
   cd backend
   pytest tests/integration/
   ```

## Key Configuration
- Default port: 8000 for backend, 3000 for frontend
- Qdrant collection: `textbook_content`
- Database schema: `rag_chatbot`
- Text chunk size: 512 tokens
- Embedding model: `text-embedding-3-small`

## Development Workflow
1. Make code changes
2. Run tests: `pytest tests/`
3. Verify API contracts are maintained
4. Update documentation as needed
5. Commit with conventional commits format

## Troubleshooting
- If Qdrant connection fails, verify API key and URL
- If embeddings are slow, check API rate limits
- If authentication fails, verify BetterAuth configuration
- For Docusaurus integration issues, check plugin configuration

## Outcome

- ✅ Impact: Created comprehensive implementation plan with architecture, research, data models, and quickstart guide
- 🧪 Tests: none
- 📁 Files: Created plan.md, research.md, data-model.md, quickstart.md, and contracts/rag-api.yaml
- 🔁 Next prompts: Task generation can now proceed based on this implementation plan
- 🧠 Reflection: Plan addresses all requested architecture decisions and provides a clear path for implementation

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS - plan meets all requirements
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Generate tasks based on this implementation plan