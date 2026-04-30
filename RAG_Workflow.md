# 🔁 System Workflow – RAG-Based AI Assistant

## 📌 Overview
This document describes the end-to-end workflow of the RAG system, from user query to final response generation.

---

## 🧠 1. Query Processing

User submits a query via frontend UI.

Steps:
- Generate session_id (UUID)
- Send request to FastAPI backend
- Check cache (if enabled)

---

## 🔍 2. Query Routing

System determines:
- Greeting / casual query → Direct LLM response
- Knowledge query → RAG pipeline

---

## 📚 3. Retrieval Phase

Hybrid retrieval is applied:

- BM25 search (keyword-based)
- Vector search (semantic similarity)

Top 20 documents retrieved

---

## 🧮 4. Reranking

- Apply cross-encoder reranker
- Rank documents by relevance

Top 5 documents selected

---

## ✂️ 5. Context Preparation

- Extract relevant chunks
- Apply semantic chunking (if enabled)
- Format context for LLM prompt

---

## 🤖 6. LLM Generation

- Input: User query + retrieved context
- Model generates response
- Ensures:
  - Grounded answers
  - Minimal hallucination

---

## ⚡ 7. Streaming Response

- Backend streams response (SSE)
- Frontend displays:
  - Typing effect
  - Partial responses

---

## 📎 8. Source Attribution

- Attach document metadata
- Show:
  - File name
  - Page reference

---

## 💾 9. Memory Handling

- Store chat history in Redis
- Maintain session-based context

---

## 🔄 Final Flow

User → API → Cache → Retrieval → Rerank → LLM → Stream → UI

---

## 🚀 Key Features

- Hybrid Retrieval (BM25 + Vector)
- Semantic Chunking (optional)
- Real-time Streaming
- Redis-based Memory
- Source Citation

---

## 📈 Future Enhancements

- Evaluation Metrics (Recall@K, Faithfulness)
- Feedback Loop (user rating)
- Multi-document reasoning
- GPU acceleration
