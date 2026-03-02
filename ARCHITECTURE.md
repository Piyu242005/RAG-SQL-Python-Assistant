# RAG System Architecture

## Overview

This RAG (Retrieval-Augmented Generation) system combines document retrieval with language model generation to answer questions about SQL and Python using PDF handbooks.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           User Interface                              │
│                     (React + Tailwind CSS)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ Chat Input   │  │ Message List │  │ Source Cards │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└────────────────────────────┬─────────────────────────────────────────┘
                             │ HTTP/REST API
┌────────────────────────────▼─────────────────────────────────────────┐
│                        FastAPI Backend                                │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    API Endpoints                             │   │
│  │  /api/chat  │  /api/health  │  /api/documents              │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                             │                                         │
│  ┌─────────────────────────▼──────────────────────────────────┐    │
│  │                   RAG Pipeline                              │    │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐          │    │
│  │  │  Retriever │→ │  Formatter │→ │  Generator │          │    │
│  │  └────────────┘  └────────────┘  └────────────┘          │    │
│  └───────┬──────────────────────────────────┬─────────────────┘    │
└──────────┼──────────────────────────────────┼──────────────────────┘
           │                                   │
           ▼                                   ▼
┌──────────────────────────┐      ┌───────────────────────────┐
│   Vector Store           │      │   Ollama (Local LLM)      │
│   (ChromaDB)             │      │                           │
│  ┌────────────────────┐  │      │  ┌─────────────────────┐ │
│  │ Embeddings        │  │      │  │  llama2 / mistral   │ │
│  │ (HuggingFace)     │  │      │  │  (Running locally)  │ │
│  └────────────────────┘  │      │  └─────────────────────┘ │
│  ┌────────────────────┐  │      └───────────────────────────┘
│  │ Document Chunks   │  │
│  │ (from PDFs)       │  │
│  └────────────────────┘  │
└──────────────────────────┘
           ▲
           │ Initial Processing
┌──────────┴───────────────┐
│  Document Processor      │
│  (PyMuPDF + LangChain)   │
│  ┌────────────────────┐  │
│  │ PDF Extraction    │  │
│  │ Text Chunking     │  │
│  │ Metadata Extract  │  │
│  └────────────────────┘  │
│                          │
│  Input: PDF Files        │
│  - MySQL Handbook.pdf    │
│  - Python Handbook.pdf   │
└──────────────────────────┘
```

## Component Descriptions

### 1. Frontend (React)

**Purpose**: Provide user interface for chat interactions

**Components**:
- `ChatContainer`: Main layout and orchestration
- `ChatMessage`: Display user/AI messages with Markdown/code support
- `ChatInput`: Text input with document type filtering
- `SourceCard`: Display PDF source citations

**Tech Stack**:
- React 18
- Vite (build tool)
- Tailwind CSS (styling)
- Axios (API client)
- React Markdown (message rendering)
- React Syntax Highlighter (code display)

### 2. Backend (FastAPI)

**Purpose**: API server and RAG orchestration

**Modules**:

#### `main.py`
- FastAPI application setup
- CORS configuration
- API endpoint definitions
- Health checks

#### `rag_pipeline.py`
- Core RAG logic
- Document retrieval
- Context formatting
- LLM invocation
- Response parsing

#### `vector_store.py`
- ChromaDB management
- Embedding generation
- Similarity search
- MMR (Maximum Marginal Relevance) retrieval

#### `document_processor.py`
- PDF text extraction (PyMuPDF)
- Semantic chunking
- Metadata extraction
- Document object creation

#### `llm_config.py`
- Ollama connection management
- Model validation
- Generation parameters

#### `models.py`
- Pydantic models for request/response validation

**Tech Stack**:
- FastAPI
- LangChain
- ChromaDB
- Ollama Python client
- HuggingFace Transformers
- PyMuPDF

### 3. Vector Store (ChromaDB)

**Purpose**: Store and retrieve document embeddings

**Features**:
- Persistent storage (SQLite)
- Metadata filtering (doc_type: mysql/python)
- Similarity search with scores
- MMR for diverse results

**Embedding Model**:
- `sentence-transformers/all-MiniLM-L6-v2`
- 384-dimensional embeddings
- Optimized for semantic similarity

### 4. LLM (Ollama)

**Purpose**: Generate natural language responses

**Supported Models**:
- llama2 (default)
- mistral (recommended for speed)
- llama3 (better quality)

**Configuration**:
- Temperature: 0.3 (factual responses)
- Context window: 2048 tokens
- Local execution (no API calls)

## Data Flow

### Initialization Phase (One-time)

```
1. PDF Files
   ↓
2. Document Processor
   - Extract text from PDFs
   - Split into chunks (1000 chars, 200 overlap)
   - Add metadata (source, page, doc_type)
   ↓
3. Vector Store
   - Generate embeddings (HuggingFace)
   - Store in ChromaDB
   - Persist to disk
```

### Query Phase (Runtime)

```
1. User enters question
   ↓
2. Frontend sends POST /api/chat
   ↓
3. Backend receives query
   ↓
4. RAG Pipeline:
   a. Retriever: Query vector store (similarity + MMR)
   b. Get top 4 relevant chunks
   c. Format context with sources
   d. Build prompt with context + question
   e. Send to Ollama LLM
   f. Parse response
   ↓
5. Return answer + sources
   ↓
6. Frontend displays formatted response
```

## Configuration

### Chunking Strategy

- **Chunk Size**: 1000 characters
- **Overlap**: 200 characters
- **Separators**: `["\n\n", "\n", ". ", " "]`
- **Rationale**: Preserves code blocks and context

### Retrieval Strategy

- **Search Type**: MMR (Maximum Marginal Relevance)
- **K**: 4 documents
- **Rationale**: Balance between relevance and diversity

### LLM Parameters

- **Temperature**: 0.3
- **Max Tokens**: 1000
- **Rationale**: Factual, concise responses

## Security Considerations

1. **CORS**: Configured for localhost only (development)
2. **Input Validation**: Pydantic models validate all inputs
3. **Error Handling**: Graceful error messages without stack traces
4. **Local Processing**: No data leaves the machine

## Performance Optimization

1. **Singleton Pattern**: RAG pipeline initialized once
2. **Persistent Vector Store**: No re-embedding on restart
3. **Async Endpoints**: Non-blocking API calls
4. **Efficient Chunking**: Balanced chunk size for retrieval quality

## Scalability

### Current Limitations

- Single-threaded Ollama (sequential queries)
- In-memory vector search (ChromaDB loads to RAM)
- Development server (Uvicorn)

### Production Improvements

1. **Backend**:
   - Gunicorn with multiple workers
   - Redis for caching
   - PostgreSQL for vector store (pgvector)

2. **Frontend**:
   - Production build (`npm run build`)
   - CDN hosting
   - Service worker for offline support

3. **LLM**:
   - vLLM for batched inference
   - Model quantization (GGUF)
   - GPU acceleration

## Monitoring

### Health Endpoint (`/api/health`)

Returns:
- Ollama status
- Model availability
- Vector store status
- Available models

### Logging

- Application logs: `backend/main.py`
- Ollama logs: Ollama process
- Frontend: Browser console

## Testing Strategy

1. **Unit Tests**: Individual module testing
2. **Integration Tests**: RAG pipeline end-to-end
3. **Manual Testing**: Sample queries with expected results

## Future Enhancements

1. **Conversation Memory**: Multi-turn conversations
2. **Hybrid Search**: BM25 + semantic search
3. **Reranking**: Cross-encoder for better results
4. **Streaming**: Real-time response streaming
5. **Multi-Language**: Support for more programming languages
6. **Upload Feature**: Allow users to add their own PDFs

---

For implementation details, see individual module source code.
