<div align="center">

# ✨ Aurora — RAG SQL & Python Assistant

**An AI-powered, privacy-first assistant that answers SQL & Python questions from PDF handbooks using local LLMs.**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-000000?style=flat-square&logo=ollama&logoColor=white)](https://ollama.ai)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

[Getting Started](#-getting-started) · [Architecture](#-architecture) · [API Reference](#-api-reference) · [Contributing](#-contributing)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Screenshots](#-screenshots)
- [Getting Started](#-getting-started)
- [Usage](#-usage)
- [Architecture](#-architecture)
- [API Reference](#-api-reference)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [Acknowledgements](#-acknowledgements)
- [License](#-license)

---

## 🧠 Overview

**Aurora** is a production-grade **Retrieval-Augmented Generation (RAG)** system that provides intelligent question-answering for **MySQL** and **Python** programming using local PDF handbooks. It runs entirely on your machine — no API keys, no cloud costs, no data leaks.

> Ask a question → Aurora searches the handbooks → Returns an accurate answer with page-level source citations.

---

## 🚀 Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **Intelligent Q&A** | Ask questions about SQL or Python and get accurate, context-aware answers |
| 🔒 **100% Local & Private** | Runs entirely on your machine via Ollama — zero API costs, zero data leaks |
| 📄 **Source Citations** | Every answer includes PDF name + page number for verification |
| 🔍 **Semantic Search** | ChromaDB vector store with HuggingFace embeddings for precise retrieval |
| 🎯 **Document Filtering** | Filter to MySQL only, Python only, or search both |
| 💬 **Premium Chat UI** | Dark-mode glassmorphism interface with animations, sidebar, and code copy |
| ⚡ **Fast Setup** | One-command setup script gets you running in ~5 minutes |

---

## 📸 Screenshots

<div align="center">

| Welcome Screen | Chat in Action |
|:-:|:-:|
| ![Welcome](https://via.placeholder.com/400x260/0f172a/6366f1?text=Welcome+Screen) | ![Chat](https://via.placeholder.com/400x260/0f172a/6366f1?text=Chat+Demo) |

> *Replace with actual screenshots after running the app locally.*

</div>

---

## 🏁 Getting Started

### Prerequisites

| Tool | Version | Link |
|------|---------|------|
| Python | 3.8+ | [python.org](https://www.python.org/) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org/) |
| Ollama | Latest | [ollama.ai](https://ollama.ai/) |

You also need these PDFs in the project root:
- `MySQL Handbook.pdf`
- `The Ultimate Python Handbook.pdf`

### Quick Setup (Recommended)

**Windows:**
```powershell
.\setup.bat
```

**Linux / macOS:**
```bash
chmod +x setup.sh && ./setup.sh
```

The script automatically installs dependencies, configures Ollama, processes PDFs, and validates everything.

### Manual Setup

<details>
<summary>Click to expand manual steps</summary>

#### 1. Start Ollama & pull a model

```bash
ollama serve            # Terminal 1
ollama pull llama2      # Terminal 2 — or `mistral` for faster responses
```

#### 2. Backend

```bash
cd backend
python -m venv venv

# Activate
venv\Scripts\activate     # Windows
source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
copy .env.example .env    # Windows (or `cp` on Unix)
python initialize_db.py   # Process PDFs → vector store
```

#### 3. Frontend

```bash
cd frontend
npm install
```

</details>

---

## 🎮 Usage

### Running the App

Open **three terminals**:

```bash
# Terminal 1 — Ollama (skip if running as service)
ollama serve

# Terminal 2 — Backend
cd backend && venv\Scripts\activate && python main.py
# → http://localhost:8000

# Terminal 3 — Frontend
cd frontend && npm run dev
# → http://localhost:5173
```

### Demo Queries

**SQL:**
```
What are SQL JOINs and when should I use each type?
How do I create a MySQL table with constraints?
Explain the SELECT statement with examples
```

**Python:**
```
How do I create a Python class with inheritance?
What are list comprehensions and how do they work?
Explain Python decorators with examples
```

> **Tip:** Use the filter chips (All / MySQL / Python) to narrow results to a specific handbook.

---

## 🏗 Architecture

```
┌─────────────┐       ┌──────────────────┐       ┌──────────────┐
│   React UI  │──────→│  FastAPI Backend  │──────→│   Ollama     │
│  (Vite +    │  REST │                  │ Local │  (llama2 /   │
│  Tailwind)  │←──────│  RAG Pipeline    │←──────│   mistral)   │
└─────────────┘       └────────┬─────────┘       └──────────────┘
                               │
                     ┌─────────▼─────────┐
                     │    ChromaDB       │
                     │  Vector Store     │
                     │  (HuggingFace     │
                     │   Embeddings)     │
                     └───────────────────┘
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18, Tailwind CSS, Framer Motion | Premium dark-mode chat UI |
| **Backend** | FastAPI, LangChain, Pydantic | API server & RAG orchestration |
| **Vector DB** | ChromaDB, HuggingFace Embeddings | Semantic document search |
| **LLM** | Ollama (llama2 / mistral) | Local language model inference |
| **PDF Processing** | PyMuPDF, LangChain Text Splitters | Extract & chunk PDF content |

### Project Structure

```
aurora-rag/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── rag_pipeline.py         # Core RAG chain logic
│   ├── vector_store.py         # ChromaDB management
│   ├── document_processor.py   # PDF extraction & chunking
│   ├── llm_config.py           # Ollama configuration
│   ├── models.py               # Pydantic schemas
│   ├── initialize_db.py        # One-time DB setup
│   └── routers/chat.py         # Chat API endpoints
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx         # Collapsible sidebar
│   │   │   ├── ChatContainer.jsx   # Main chat layout
│   │   │   ├── ChatMessage.jsx     # Animated message bubbles
│   │   │   ├── ChatInput.jsx       # Auto-resize input bar
│   │   │   ├── CodeBlock.jsx       # Syntax highlight + copy
│   │   │   ├── SourceCard.jsx      # Expandable citations
│   │   │   ├── TypingIndicator.jsx # Loading animation
│   │   │   └── ToastProvider.jsx   # Toast notifications
│   │   ├── hooks/useChat.js        # Chat state management
│   │   ├── services/api.js         # Axios API client
│   │   ├── App.jsx                 # Root component
│   │   └── index.css               # Design system
│   └── tailwind.config.js
│
├── MySQL Handbook.pdf
├── The Ultimate Python Handbook.pdf
├── setup.bat / setup.sh
└── README.md
```

---

## 📡 API Reference

### `POST /api/chat` — Send a query

**Request:**
```json
{
  "query": "What is a SQL JOIN?",
  "doc_type": "mysql"
}
```
> `doc_type` is optional — omit to search all documents.

**Response:**
```json
{
  "answer": "A SQL JOIN clause combines rows from two or more tables...",
  "sources": [
    {
      "source": "MySQL Handbook.pdf",
      "page": 42,
      "doc_type": "mysql",
      "content_preview": "JOIN operations allow you to..."
    }
  ],
  "success": true
}
```

### `GET /api/health` — System status

Returns Ollama status, model availability, and vector store health.

### `GET /api/documents` — Document statistics

Returns counts and metadata about indexed documents.

### `POST /api/initialize` — Reinitialize system

Reprocesses PDFs and rebuilds the vector store.

> 📘 **Interactive docs:** Visit `http://localhost:8000/docs` for the Swagger UI.

---

## ⚙️ Configuration

### Backend (`.env`)

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2                              # or mistral, llama3
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

### Frontend

The API base URL defaults to `http://localhost:8000` and can be overridden via the `VITE_API_URL` env variable.

---

## 🐛 Troubleshooting

<details>
<summary><strong>Ollama is not running</strong></summary>

```bash
ollama serve
```
</details>

<details>
<summary><strong>Model not found</strong></summary>

```bash
ollama pull llama2    # or: ollama pull mistral
```
</details>

<details>
<summary><strong>Vector store not initialized</strong></summary>

```bash
cd backend
venv\Scripts\activate   # or source venv/bin/activate
python initialize_db.py
```
</details>

<details>
<summary><strong>Frontend can't connect to backend</strong></summary>

- Ensure backend is running on port `8000`
- Check CORS settings in `backend/config.py`
- Verify proxy in `frontend/vite.config.js`
</details>

<details>
<summary><strong>Slow responses</strong></summary>

- Use a faster model: `ollama pull mistral`
- Reduce `k` in `backend/rag_pipeline.py`
- Increase `CHUNK_SIZE` in `.env`
</details>

---

## 🗺️ Roadmap

- [ ] 🔄 Streaming responses (real-time token output)
- [ ] 💾 Conversation memory (multi-turn context)
- [ ] 🔍 Hybrid search (BM25 + semantic)
- [ ] 📤 User PDF uploads
- [ ] 🌐 Multi-language support
- [ ] 🧪 Automated test suite
- [ ] 🐳 Docker Compose deployment
- [ ] 📊 Usage analytics dashboard

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feat/my-feature`
3. **Commit** with clear messages: `git commit -m "feat: add streaming responses"`
4. **Push** and open a **Pull Request**

### Code Style

- **Python:** Follow PEP 8, use type hints, write docstrings
- **JavaScript/React:** Functional components, hooks, ES6+
- **CSS:** Tailwind utility classes, use design tokens from `tailwind.config.js`
- **Commits:** Use [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`)

---

## 🙏 Acknowledgements

| Tool | Role |
|------|------|
| [LangChain](https://langchain.com) | RAG framework & chain orchestration |
| [Ollama](https://ollama.ai) | Local LLM runtime |
| [ChromaDB](https://www.trychroma.com) | Vector database |
| [FastAPI](https://fastapi.tiangolo.com) | Backend framework |
| [React](https://react.dev) | Frontend library |
| [Tailwind CSS](https://tailwindcss.com) | Utility-first CSS |
| [Framer Motion](https://www.framer.com/motion) | Animations |
| [HuggingFace](https://huggingface.co) | Embedding models |

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ by [Piyu](https://github.com/Piyu242005)**

⭐ Star this repo if you found it useful!

</div>
