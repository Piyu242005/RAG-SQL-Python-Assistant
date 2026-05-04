# � API Reference

The backend operates on `http://localhost:8000`. All protected endpoints require the header `x-api-key`.

## Authentication
**Header:** `x-api-key: your_secret_key_123`

---

### 1. Standard Chat (Synchronous)
`POST /api/chat`

**Request:**
```json
{
  "query": "How do I create a database in MySQL?",
  "doc_type": "mysql",
  "conversation_id": "session_123"
}
```

**Response:**
```json
{
  "answer": "To create a database in MySQL, use the `CREATE DATABASE` statement...",
  "sources": [{"source": "MySQL Handbook.pdf", "page": 12}],
  "success": true
}
```

---

### 2. Stream Chat (Asynchronous SSE)
`POST /api/chat/stream`

Streams the LLM response in real-time. Yields chunked tokens and a final `[DONE]` marker.

**Request:** Same payload as synchronous chat.
**Response (Event Stream):**
```text
data: {"sources": [{"source": "MySQL Handbook.pdf"}]}
data: {"token": "To"}
data: {"token": " create"}
data: [DONE]
```

---

### 3. Re-index Vector Database
`POST /api/reindex`

Force a teardown and complete re-embedding sequence of all PDFs in the data folder.

**Response:**
```json
{
  "status": "reindexed"
}
```

---

### 4. Health Check
`GET /api/health`

Public endpoint to verify system stability.

**Response:**
```json
{
  "ollama_running": true,
  "vectorstore_initialized": true,
  "redis_connected": true
}
```
