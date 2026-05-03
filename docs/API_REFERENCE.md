# 📡 API Reference v1.0

> **Standard REST API for interacting with the Piyu AI Assistant. All endpoints return JSON unless otherwise specified.**

---

## 🔑 Authentication

All `/api` endpoints (except `/api/health`) require an API Key passed in the headers.

| Header | Value |
|:---|:---|
| `x-api-key` | Your configured secret key (Default: `your_secret_key_123`) |

---

## 💬 Chat Endpoints

### 1. Streaming Chat (Recommended)
`POST /api/chat/stream`

Streams the LLM response token-by-token using Server-Sent Events (SSE).

**Request Body:**
```json
{
  "query": "How do I use SQL JOINs?",
  "conversation_id": "optional_session_uuid",
  "doc_type": "mysql" 
}
```
*`doc_type` can be `mysql`, `python`, or `null`.*

**Response Stream:**
1. `{"sources": [...]}`: Initial metadata containing document references.
2. `{"token": "..."}`: Individual text tokens.
3. `[DONE]`: Signal that the stream has finished.

---

### 2. Standard Chat
`POST /api/chat`

Returns the full answer in a single JSON response.

**Request Body:** Same as streaming.

**Response:**
```json
{
  "answer": "...",
  "sources": [...],
  "success": true
}
```

---

## 🛠️ System Endpoints

### 3. Health Check
`GET /api/health`

**Security:** Public

**Response:**
```json
{
  "status": "healthy",
  "ollama_running": true,
  "model_available": true,
  "vectorstore_initialized": true,
  "configured_model": "llama3.2"
}
```

---

### 4. System Initialization
`POST /api/initialize`

Triggers the ingestion pipeline to process all PDFs and rebuild the vector database.

**Response:**
```json
{
  "success": true,
  "message": "System initialized successfully",
  "documents_processed": 178
}
```

---

## 📂 Document Endpoints

### 5. Document Statistics
`GET /api/documents`

**Response:**
```json
{
  "total_documents": 178,
  "persist_directory": "./chroma_db",
  "embedding_model": "..."
}
```

### 6. Upload PDF
`POST /api/upload`

Uploads and immediately indexes a new PDF.

**Form Data:**
- `file`: The PDF file.
- `doc_type`: Category for the file (default: `custom`).
