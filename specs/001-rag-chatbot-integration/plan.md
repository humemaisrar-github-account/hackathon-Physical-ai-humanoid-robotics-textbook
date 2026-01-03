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