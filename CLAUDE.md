# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Environment Setup:**
```bash
uv sync                    # Install dependencies
cp .env.example .env       # Create environment file (add ANTHROPIC_API_KEY)
```

**Running the Application:**
```bash
./run.sh                   # Quick start (makes run.sh executable and starts server)
cd backend && uv run uvicorn app:app --reload --port 8000  # Manual start
```

**Access Points:**
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Architecture Overview

This is a **RAG (Retrieval-Augmented Generation) chatbot** for course materials using FastAPI backend, vanilla JS frontend, ChromaDB vector storage, and Anthropic Claude.

**Core Architecture Pattern:**
```
RAGSystem (orchestrator)
├── DocumentProcessor (structured parsing + chunking)
├── VectorStore (dual ChromaDB collections)
├── AIGenerator (Claude with function calling)
├── SessionManager (conversation history)
└── ToolManager (AI-invoked search tools)
```

**Dual Collection Strategy:**
- `course_catalog`: Course metadata for semantic name resolution
- `course_content`: Actual content chunks with embeddings

**Tool-Based Search Pattern:**
The AI uses function calling to autonomously invoke `search_course_content(course_name, query)` rather than traditional retrieval. This enables:
- Semantic course name matching with fuzzy resolution
- Context-aware search within specific courses
- Natural conversation flow with tool invocation

## Document Processing Pipeline

**Expected Document Structure:**
```
Course Title: [title]
Course Link: [url]
Course Instructor: [instructor]

Lesson 0: Introduction
Lesson Link: [optional]
[content...]

Lesson 1: Next Topic
[content...]
```

**Chunking Strategy:**
- Sentence-boundary aware splitting (800 chars, 100 overlap)
- Context enhancement: `"Course {title} Lesson {N} content: {chunk}"`
- Preserves hierarchical metadata (course → lesson → chunk)

**Processing Flow:**
1. Metadata extraction from document headers
2. Lesson parsing with optional lesson links
3. Intelligent text chunking with overlap
4. Context enhancement with course/lesson info
5. Dual storage: metadata + content embeddings

## Key Configuration

**Environment Variables (.env required):**
```
ANTHROPIC_API_KEY=your_key_here
```

**Core Settings (backend/config.py):**
- Model: `claude-sonnet-4-20250514`
- Embedding: `all-MiniLM-L6-v2`
- Chunk Size: 800 chars (overlap: 100)
- Max Search Results: 5
- Conversation History: 2 exchanges

## Development Patterns

**Session Management:**
- Stateful conversations with configurable history
- Session IDs track user context across queries

**Error Handling:**
- UTF-8 with fallback encoding for document processing
- Graceful degradation for malformed course documents
- API responses with proper HTTP status codes

**Document Loading:**
- Auto-loads `/docs` folder on startup
- Deduplication by course title
- Supports `.pdf`, `.docx`, `.txt` files
- Incremental loading (skips existing courses)

**Frontend Architecture:**
- Vanilla JavaScript with Marked.js for markdown rendering
- Session-based chat interface with source display
- Real-time streaming responses

## Dependencies

**Core Runtime:**
- `chromadb` - Vector database
- `anthropic` - Claude API client  
- `sentence-transformers` - Text embeddings
- `fastapi` + `uvicorn` - Web framework + server
- `python-dotenv` - Environment loading

**Package Management:**
- Uses `uv` (not pip) for dependency management
- Python 3.13+ required
- Dependencies locked in `uv.lock`