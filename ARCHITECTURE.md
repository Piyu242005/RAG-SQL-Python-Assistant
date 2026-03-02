# 🏗 Aurora — System Architecture

> Technical deep-dive into how the RAG system is designed, how data flows, and how each component works together.

---

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                          │
│  Sidebar │ ChatContainer │ ChatInput │ ChatMessage │ SourceCard │
└────────────────────────────┬─────────────────────────────────────┘
                             │ REST API (HTTP)
┌────────────────────────────▼─────────────────────────────────────┐
│                     FastAPI Backend                               │
│                                                                   │
│   /api/chat  ─→  RAG Pipeline ─→  Retriever ─→ Context Builder  │
│   /api/health                     │                    │         │
│   /api/documents                  ▼                    ▼         │
│   /api/initialize          ChromaDB Search      Ollama LLM      │
│                            (Semantic)           (Generation)     │
└──────────┬───────────────────────────────────────┬───────────────┘
           │                                       │
┌──────────▼──────────┐               ┌────────────▼──────────────┐
│   ChromaDB          │               │   Ollama                  │
│   Vector Store      │               │   Local LLM Runtime       │
│                     │               │                           │
│   • HuggingFace     │               │   • llama2 (default)      │
│     Embeddings      │               │   • mistral (fast)        │
│   • 384-dim vectors │               │   • llama3 (quality)      │
│   • SQLite persist  │               │                           │
└──────────▲──────────┘               └───────────────────────────┘
           │
┌──────────┴──────────┐
│  Document Processor │
│  (One-time Setup)   │
│                     │
│  PyMuPDF → Chunk    │
│  → Embed → Store    │
│                     │
│  Input:             │
│  • MySQL Handbook   │
│  • Python Handbook  │
└─────────────────────┘
```

---

## Component Details

### 1. Frontend

| Module | File | Role |
|--------|------|------|
| Sidebar | `Sidebar.jsx` | Collapsible panel with history, filters, new chat |
| Chat Container | `ChatContainer.jsx` | Message list, welcome screen, typing indicator |
| Chat Input | `ChatInput.jsx` | Auto-resize input, filter chips, keyboard shortcuts |
| Chat Message | `ChatMessage.jsx` | Animated bubbles, markdown, code blocks |
| Code Block | `CodeBlock.jsx` | Syntax highlighting + copy-to-clipboard |
| Source Card | `SourceCard.jsx` | Expandable citation cards |
| Typing Indicator | `TypingIndicator.jsx` | Animated 3-dot loader |
| Chat Hook | `useChat.js` | State management, conversation history |
| API Client | `api.js` | Axios wrapper for all endpoints |

**Stack:** React 18 · Vite · Tailwind CSS 3 · Framer Motion · Lucide Icons

---

### 2. Backend

| Module | File | Role |
|--------|------|------|
| Entry Point | `main.py` | FastAPI app, CORS, health checks |
| RAG Pipeline | `rag_pipeline.py` | Retrieval → Context → Generation chain |
| Vector Store | `vector_store.py` | ChromaDB CRUD, similarity/MMR search |
| Doc Processor | `document_processor.py` | PDF extraction, chunking, metadata |
| LLM Config | `llm_config.py` | Ollama connection, model validation |
| Schemas | `models.py` | Pydantic request/response models |
| Chat Router | `routers/chat.py` | `/api/chat` endpoint logic |

**Stack:** FastAPI · LangChain · ChromaDB · Ollama · PyMuPDF · HuggingFace

---

### 3. Vector Store (ChromaDB)

| Property | Value |
|----------|-------|
| Embedding Model | `sentence-transformers/all-MiniLM-L6-v2` |
| Dimensions | 384 |
| Persistence | SQLite on disk |
| Search Types | Similarity + MMR (Maximum Marginal Relevance) |
| Metadata Filters | `doc_type: "mysql" \| "python"` |

---

### 4. LLM (Ollama)

| Property | Value |
|----------|-------|
| Default Model | `llama2` |
| Temperature | `0.3` (factual) |
| Context Window | 2048 tokens |
| Execution | 100% local — no API calls |

---

## Data Flow

### Initialization (One-time)

```
PDF Files
  ↓
Document Processor
  • Extract text (PyMuPDF)
  • Split into 1000-char chunks (200 overlap)
  • Tag metadata (source, page, doc_type)
  ↓
Vector Store
  • Generate 384-dim embeddings (HuggingFace)
  • Store in ChromaDB
  • Persist to disk
```

### Query (Runtime)

```
1. User enters question
2. Frontend → POST /api/chat { query, doc_type? }
3. RAG Pipeline:
   a. Retrieve top-4 relevant chunks (MMR search)
   b. Format context with source metadata
   c. Build prompt: context + question
   d. Send to Ollama LLM
   e. Parse response
4. Return { answer, sources[] }
5. Frontend renders animated response + citation cards
```

---

## Configuration

### Chunking Strategy

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Chunk Size | 1000 chars | Preserves code blocks and context |
| Overlap | 200 chars | Prevents losing info at boundaries |
| Separators | `\n\n`, `\n`, `. `, ` ` | Respects natural document structure |

### Retrieval Strategy

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Search Type | MMR | Balances relevance and diversity |
| k | 4 documents | Enough context without overwhelming LLM |

---

## Security

- **CORS:** Localhost-only in development
- **Input Validation:** Pydantic models on all endpoints
- **Error Handling:** Graceful messages, no stack traces exposed
- **Privacy:** All data stays on machine — nothing leaves

---

## Performance

| Metric | Typical Value |
|--------|--------------|
| PDF Processing | 2–5 min (one-time) |
| Embedding Generation | 3–8 min (one-time) |
| Query Response | 5–15 sec |
| RAM Usage | ~2–4 GB (llama2) |

### Optimizations

- Singleton RAG pipeline (initialized once)
- Persistent vector store (no re-embedding on restart)
- Async FastAPI endpoints
- Efficient MMR retrieval

---

## Production Scaling

| Area | Improvement |
|------|-------------|
| **Backend** | Gunicorn + workers, Redis cache, pgvector |
| **Frontend** | `npm run build` → CDN, service worker |
| **LLM** | vLLM batching, GGUF quantization, GPU acceleration |

---

## Future Enhancements

| Feature | Status |
|---------|--------|
| Streaming responses | 🔜 Planned |
| Conversation memory | 🔜 Planned |
| Hybrid search (BM25 + semantic) | 🔜 Planned |
| User PDF uploads | 🔜 Planned |
| Cross-encoder reranking | 💡 Considered |
| Multi-language docs | 💡 Considered |

---

*For setup instructions, see [QUICKSTART.md](QUICKSTART.md). For the full README, see [README.md](README.md).*
