---
id: 001
title: Update Constitution
stage: constitution
date: 2025-12-28
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: user
command: sp.constitution
labels: [constitution, documentation]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

# /sp.constitution

## Project Title
**AI-Native Textbook Enhancement with Integrated RAG Chatbot, Personalization, and Multilingual Support**

---

## Foundational Principles

- **Reliability & Accuracy**
  All implemented features must operate consistently across the deployed Docusaurus textbook without disrupting existing content or navigation.

- **Production-Oriented Engineering**
  The system must follow industry-grade architectural patterns for RAG pipelines, backend APIs, and data storage.

- **Modular & Future-Ready Design**
  The architecture should support easy extension, maintenance, and feature growth with minimal refactoring.

- **Data Security & Privacy**
  User-related data (background information, preferences, session logs) must be handled securely and responsibly.

- **Context-Aware User Experience**
  Chatbot responses must remain tightly aligned with chapter context, selected text, and retrieved source material.

---

## Implementation Standards

### Retrieval-Augmented Generation (RAG)

- The chatbot must be implemented using:
  - OpenAI Agents (Python SDK, ChatKit optional)
  - FastAPI backend
  - Neon Serverless Postgres
  - Qdrant Cloud (Free Tier)
- All generated answers must be strictly grounded in retrieved textbook content.
- The chatbot must support two interaction modes:
  1. Full-textbook question answering
  2. Selected-text-only question answering

---

### Textbook Integration

- The chatbot must be embedded directly into the Docusaurus-based textbook.
- All UI elements (chat window, buttons, controls) must visually align with the textbook's theme.
- The integration must not interrupt the reading flow or accessibility.

---

## Optional (Bonus) Features

### Authentication

- If implemented, authentication must:
  - Use **BetterAuth**
  - Collect basic software and hardware background during signup
  - Store background data for use in personalization features

---

### Chapter Personalization

- Authenticated users may access a **"Personalize Chapter"** option at the start of each chapter.
- Chapter content may be adapted or enhanced based on user background.
- Technical accuracy must be preserved at all times.

---

### Urdu Translation

- Authenticated users may access a **"Translate to Urdu"** option at the chapter level.
- Translations must preserve:
  - Technical meaning
  - Formatting and structure
  - Readability and clarity

---

## Technical Constraints

- **Frontend:** Docusaurus
- **Backend:** FastAPI
- **Database:** Neon Serverless Postgres
- **Vector Database:** Qdrant (Free Tier)
- **AI Layer:** OpenAI Agents (Python SDK, ChatKit optional)

Additional constraints:
- Bonus features must only be accessible to authenticated users.
- The complete system must be deployable on free or low-cost tiers suitable for students.

---

## Evaluation Criteria

### Core Functionality (100 Points)

- Fully functional RAG chatbot integrated into the textbook
- Support for both full-book and selected-text-only modes
- Stable, accurate, and grounded responses

-

## Response snapshot

# Constitution Update Summary

I have successfully updated the project constitution for the "AI-Native Textbook Enhancement with Integrated RAG Chatbot, Personalization, and Multilingual Support" project. Here are the details:

**New Version**: 1.1.0 (incremented from 1.0.0 - this is a minor version bump as we've added new principles and sections)

**Version Bump Rationale**: This update includes new principle additions and governance updates, which according to semantic versioning constitutes a minor version change (MAJOR: backward incompatible changes, MINOR: new principles/sections added, PATCH: clarifications/typos).

**Changes Made**:
- Updated project name from placeholder to the specified project title
- Replaced all placeholder principles with the specific principles from your input:
  - Reliability & Accuracy
  - Production-Oriented Engineering
  - Modular & Future-Ready Design
  - Data Security & Privacy
  - Context-Aware User Experience
  - Added Implementation Standards for RAG section
- Added Textbook Integration Requirements section
- Added Technical Constraints section
- Added Optional Feature Standards section
- Added Evaluation Criteria section
- Set version to 1.1.0 and last amended date to 2025-12-28
- Included TODO for ratification date since original adoption date is unknown

**Files flagged for manual follow-up**:
- .specify/templates/plan-template.md (needs constitution check section updated)
- .specify/templates/spec-template.md (needs alignment with new principles)
- .specify/templates/tasks-template.md (needs alignment with new principles)

**Suggested commit message**: `docs: amend constitution to v1.1.0 (principle additions + governance update)`

## Outcome

- ✅ Impact: Updated project constitution with specific principles for AI textbook enhancement project
- 🧪 Tests: none
- 📁 Files: Updated .specify/memory/constitution.md with new content
- 🔁 Next prompts: Feature specification and planning can now proceed based on new constitution
- 🧠 Reflection: Constitution now properly reflects the specific requirements and constraints of the AI textbook project

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS - constitution properly updated with all required elements
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Proceed with feature specification based on updated constitution