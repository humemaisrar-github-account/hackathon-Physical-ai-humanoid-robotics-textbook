---
id: "002"
title: "Correct Backend Port Configuration"
stage: "general"
date: "2026-01-01"
surface: "agent"
model: "Claude Sonnet 4.5"
feature: "none"
branch: "main"
user: "user"
command: "Correct backend port in frontend configuration"
labels: ["chatbot", "frontend", "backend", "configuration", "bug-fix"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - "frontend/src/components/PopupChatbot.jsx"
  - "backend/production_rag_chatbot.py"
tests: []
---

# Correct Backend Port Configuration

## Prompt Text
The user was experiencing issues with the chatbot not providing book-based answers. I discovered that while the production RAG chatbot was running correctly on port 8000, the frontend was still configured to connect to port 8003. I corrected the API base URL in the frontend to point to the correct port (8000).

## Response Text
Updated the API_BASE_URL in PopupChatbot.jsx from 'http://localhost:8003' to 'http://localhost:8000' to match where the production RAG chatbot is actually running. The backend is properly configured with all required environment variables (OPENROUTER_API_KEY, QDRANT_URL, QDRANT_API_KEY) and the Qdrant collection has the book embeddings. The system is now correctly set up to retrieve and respond with book-based content only.

## Outcome
The frontend now connects to the correct backend port, allowing the chatbot to properly retrieve book content and provide book-based answers as required.

## Evaluation
The port configuration has been corrected, and the system should now properly retrieve and respond with book-based content.