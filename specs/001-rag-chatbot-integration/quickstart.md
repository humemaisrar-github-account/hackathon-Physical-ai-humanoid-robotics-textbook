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