# Document Processing Pipeline Visualization

```
📁 /docs/course1_script.txt
│
│ File Structure:
│ ┌─────────────────────────────────────┐
│ │ Course Title: Python Fundamentals  │ ← Metadata extraction
│ │ Course Link: https://...           │
│ │ Course Instructor: John Doe        │
│ │                                    │
│ │ Lesson 0: Introduction             │ ← Lesson parsing
│ │ Lesson Link: https://...           │
│ │ Welcome to Python programming...   │
│ │ Python is a versatile language...  │
│ │                                    │
│ │ Lesson 1: Variables and Types      │
│ │ In this lesson we'll learn...      │ ← Content chunking
│ │ Variables store data values...     │
│ └─────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│                    DOCUMENT PROCESSOR                           │
│                                                                 │
│  1. FILE READING                                               │
│     • UTF-8 encoding with fallback                            │
│     • Error handling for malformed files                       │
│                                                                 │
│  2. METADATA EXTRACTION                                        │
│     • Parse course title, link, instructor                    │
│     • Create Course object                                     │
│                                                                 │
│  3. LESSON PARSING                                             │
│     • Identify "Lesson N:" markers                            │
│     • Extract lesson links                                     │
│     • Group content by lessons                                │
│                                                                 │
│  4. TEXT CHUNKING                                              │
│     • Sentence-based splitting (regex)                        │
│     • Configurable chunk size (default: 1000 chars)          │
│     • Overlap between chunks (default: 200 chars)            │
│     • Preserve sentence boundaries                             │
│                                                                 │
│  5. CONTEXT ENHANCEMENT                                        │
│     • Add course + lesson context to chunks                   │
│     • Format: "Course {title} Lesson {N} content: {chunk}"   │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSED OUTPUT                             │
│                                                                 │
│  Course Object:                                                │
│  ├─ title: "Python Fundamentals"                              │
│  ├─ instructor: "John Doe"                                     │
│  ├─ course_link: "https://..."                               │
│  └─ lessons: [                                                │
│      ├─ Lesson(number=0, title="Introduction", link="...")   │
│      └─ Lesson(number=1, title="Variables and Types")        │
│     ]                                                          │
│                                                                 │
│  Course Chunks:                                               │
│  ├─ CourseChunk(                                             │
│  │    content="Course Python Fundamentals Lesson 0 content:  │
│  │             Welcome to Python programming...",            │
│  │    course_title="Python Fundamentals",                   │
│  │    lesson_number=0,                                       │
│  │    chunk_index=0                                          │
│  │  )                                                        │
│  ├─ CourseChunk(                                             │
│  │    content="Python is a versatile language...",          │
│  │    lesson_number=0,                                       │
│  │    chunk_index=1                                          │
│  │  )                                                        │
│  └─ ... (more chunks)                                        │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│                     VECTOR STORE                               │
│                                                                 │
│  1. EMBEDDING GENERATION                                       │
│     • Uses sentence-transformers model                        │
│     • Converts text chunks to vector embeddings               │
│                                                                 │
│  2. CHROMADB STORAGE                                          │
│     • Course metadata stored separately                       │
│     • Content chunks with embeddings                          │
│     • Semantic search capabilities                            │
│                                                                 │
│  Storage Structure:                                            │
│  ├─ Courses Collection                                        │
│  │  └─ Course metadata (title, instructor, links)           │
│  └─ Content Collection                                        │
│     └─ Chunks with embeddings + metadata                     │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│                    READY FOR QUERIES                           │
│                                                                 │
│  User Query: "What are Python variables?"                     │
│       ↓                                                        │
│  Semantic Search → Find relevant chunks                       │
│       ↓                                                        │
│  Context + Query → Claude AI                                  │
│       ↓                                                        │
│  Generated Response with Sources                               │
└─────────────────────────────────────────────────────────────────┘
```

## Key Processing Features

**Smart Chunking Strategy:**
- Sentence boundaries preserved
- Configurable overlap prevents context loss  
- Context headers maintain lesson/course association

**Metadata Preservation:**
- Course-level info (title, instructor, links)
- Lesson-level info (number, title, links)
- Chunk-level info (index, lesson association)

**Error Handling:**
- UTF-8 fallback encoding
- Missing metadata graceful handling
- Malformed lesson markers handled

**Deduplication:**
- Existing courses skipped on reload
- Title-based duplicate detection