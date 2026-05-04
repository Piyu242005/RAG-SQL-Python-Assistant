# 🧠 RAG Workflow Architecture

This document breaks down the robust RAG (Retrieval-Augmented Generation) pipeline used in this project.

## 🔄 The Pipeline

### 1. Ingestion & Extraction
* **Source:** `.pdf` files located in `data/pdfs/`.
* **Action:** PyMuPDF parses the text.
* **Metadata:** Assigns source names, page numbers, and tags topics (`sql` or `python`).

### 2. Chunking
* **Strategy:** `RecursiveCharacterTextSplitter`.
* **Config:** 600 characters max, 200 characters overlap.
* **Reasoning:** Keeps paragraph context intact without overflowing LLM context limits.

### 3. Embeddings & Storage
* **Model:** `sentence-transformers/all-MiniLM-L6-v2`.
* **Storage:** Locally deployed `ChromaDB` (SQLite-based vector store) inside `backend/chroma_db/`.

### 4. Query Processing & Expansion (HyDE)
* When a user inputs a query, the LLM first generates a "hypothetical answer" string (HyDE).
* Both the original query and the hypothetical answer are combined to query the vector database.

### 5. Retrieval & Reranking
* **Hybrid Search:** Combines Vector Semantic Similarity (Dense) + BM25 Keyword Search (Sparse) to retrieve the top 20 candidate chunks.
* **FlashRank:** A cross-encoder model parses the top 20 chunks and strictly re-ranks them, discarding low-relevance noise and keeping the Top 5.

### 6. Context Trimming & Caching
* **Deduplication:** Duplicate string payloads are dropped.
* **Trimming:** The context is hard-trimmed against token limits (`MAX_CONTEXT_TOKENS`) to strictly eliminate truncation hallucinations.
* **Caching Check:** Redis validates if this query + context combination has been answered before.

### 7. Generation & Streaming
* **Model:** `llama3.2` via Ollama.
* **Action:** Output is streamed character-by-character (or token-by-token) back to the client via Server-Sent Events (SSE).
