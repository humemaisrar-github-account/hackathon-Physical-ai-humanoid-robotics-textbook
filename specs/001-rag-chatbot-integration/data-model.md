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