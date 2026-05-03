# 🔁 RAG Pipeline Workflow: Under the Hood

> **A detailed technical deep-dive into how Piyu AI Assistant processes natural language into grounded, high-precision answers.**

---

## 📌 The Lifecycle of a Query

Piyu implements a **Multi-Stage Retrieval & Generation** pipeline designed for accuracy and speed. Here is the step-by-step technical execution:

### 1. Intake & Security
- **Entry**: User submits a query via the React UI.
- **Middleware**: The request passes through **SlowAPI** (rate limiting) and **API Key Authentication** (`x-api-key`).
- **Caching**: The query is hashed and checked against **Redis Cache**. If a response exists and the context hasn't changed, it is returned in `<10ms`.

### 2. Multi-Vector Hybrid Retrieval
If the cache misses, the system triggers the hybrid retrieval engine:
- **BM25 Search**: Optimized for keyword matching (e.g., exact SQL commands or function names).
- **Vector Search (ChromaDB)**: Optimized for semantic meaning using `all-MiniLM-L6-v2` embeddings.
- **Fusion**: Results from both are fused. We retrieve a broad set of **20 candidate chunks** to ensure high recall.

### 3. Cross-Encoder Reranking
Retrieval is often "noisy." To solve this, we use **FlashRank**:
- **Scoring**: A Cross-Encoder model (`ms-marco-MiniLM-L-12-v2`) re-evaluates the query against each of the 20 candidates.
- **Selection**: Only the **top 5 chunks** with the highest relevance scores are selected. This dramatically reduces the risk of the LLM being confused by irrelevant text.

### 4. Context-Augmented Prompting
The selected chunks are formatted with metadata (Source + Page) and injected into the System Prompt:
- **System Instructions**: Enforce strict non-hallucination rules and professional formatting.
- **Memory Injection**: Redis-backed conversation history is retrieved and added to the prompt to maintain multi-turn context.

### 5. LLM Generation & Streaming
- **Engine**: The prompt is sent to **Ollama (Llama 3.2)**.
- **Streaming**: Tokens are streamed back to the backend and immediately forwarded to the frontend via **Server-Sent Events (SSE)**.
- **Persistence**: Once the stream completes, the final answer is saved to Redis for both history and future caching.

---

## 📊 Technical Comparison

| Feature | Standard RAG | Piyu AI Assistant (v3.0) |
|:---|:---:|:---:|
| **Retrieval** | Single-vector search | **Hybrid (Vector + BM25)** |
| **Precision** | Top-K only | **Cross-Encoder Reranking** |
| **Latency** | Dependent on LLM | **Redis Caching (<10ms for hits)** |
| **Memory** | In-memory only | **Persistent Redis Memory** |
| **Citations** | General links | **Page-Level PDF References** |

---

## 🛡️ Anti-Hallucination Design

Piyu uses three layers of defense against hallucinations:
1.  **Strict Prompting**: The system is instructed to say "I don't know" if the answer isn't in the context.
2.  **Verified Context**: By using reranking, we ensure the context provided to the LLM is actually relevant to the specific question.
3.  **Source Grounding**: Every answer is forced to cite its source, allowing users to verify facts with a single click.

---

## 📁 Data Ingestion Pipeline

To prepare documents for the RAG pipeline, the system performs a one-time indexing:
1.  **Extraction**: `PyMuPDF` extracts raw text and coordinates from PDFs.
2.  **Chunking**: `RecursiveCharacterTextSplitter` splits text into 800-token chunks with 150-token overlap.
3.  **Embedding**: Chunks are transformed into 384-dimensional vectors.
4.  **Indexing**: Vectors are stored in ChromaDB, and text is indexed in the BM25 engine.
