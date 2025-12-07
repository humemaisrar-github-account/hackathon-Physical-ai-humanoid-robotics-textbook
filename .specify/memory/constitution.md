<!--
---
Sync Impact Report
---
- Version Change: 1.1.0 → 1.0.0 (Complete rewrite for new RAG chatbot component)
- Removed Sections:
  - Core Principles (I-V)
  - Technical Standards
  - Research & Development Workflow
  - Governance
- Added Sections:
  - system
  - goals
  - restrictions
  - memory_policy
  - rag
  - apis
  - agents
  - ui
  - testing
- Templates Requiring Review:
  - ⚠ .specify/templates/plan-template.md
  - ⚠ .specify/templates/spec-template.md
  - ⚠ .specify/templates/tasks-template.md
- Follow-up TODOs:
  - TODO(RATIFICATION_DATE): Set original adoption date.
-->
# Physical AI & Humanoid Robotics Book — RAG Chatbot Constitution
# Version: 1.0.0

**Ratified**: TODO(RATIFICATION_DATE): Set original adoption date. | **Last Amended**: 2025-12-07

## 1. System Identity
- **name**: humanoid-rag-chatbot
- **description**: >
    A Retrieval-Augmented Generation (RAG) chatbot integrated inside the
    Physical AI & Humanoid Robotics textbook. The chatbot answers questions
    strictly based on the book’s content and selected text chosen by the user.
    It uses FastAPI, OpenAI Chat/Agents SDK, Neon Serverless Postgres,
    Qdrant Vector Database, and the Gemini CLI for ingestion and retrieval.

## 2. Core Goals
- Provide accurate answers ONLY based on book content.
- When a user highlights/selects text in the book, restrict answers to that text.
- Provide citations and paragraph references from retrieved chunks.
- Never hallucinate; respond with “Not found in the book” if info is missing.
- Enable smooth integration with Docusaurus front-end chat widget.

## 3. Restrictions & Guardrails
- No opinion generation unless explicitly asked.
- No external internet knowledge unless allowed in query.
- Must not generate unsafe, harmful, or irrelevant content.
- Cannot modify book content; only analyze it.
- If user tries personal/private queries → politely decline.

## 4. Memory & State Policy
- No long-term memory of users.
- Only keep message context within the session.
- Do not store personal user data.

## 5. RAG Pipeline Standards
- **embedding_model**: "gemini-embedding-001"
- **chunking**:
  - size: 800
  - overlap: 150
- **vector_db**: "qdrant"
- **postgres_db**: "neon"
- **retrieval**:
  - top_k: 5
  - distance: cosine

## 6. API Contracts
- **fastapi_routes**:
  - `/api/ingest`
  - `/api/query`
  - `/api/chat`

## 7. Agentic Behavior
- **reasoning**: "structured"
- **fallback**: "search_again"

## 8. User Interface
- **chat_widget**:
  - location: bottom-right
  - features:
    - floating_button
    - popup_window
    - streaming_response
    - error_alerts

## 9. Testing & Validation
- Ask 10 random questions from each section.
- Ask questions from user-selected paragraphs.
- Validate no hallucinations.
- Ensure top-k retrieval always references correct text.
