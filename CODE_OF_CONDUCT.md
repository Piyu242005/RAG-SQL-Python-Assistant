# 📖 Project Guide — Piyu RAG · SQL & Python AI Assistant

> **Complete instructions for running, configuring, evaluating, and contributing to this project.**

---

## 🌟 What Is This Project?

**Piyu RAG v2.0** is a fully local, privacy-first AI assistant that answers questions about **MySQL** and **Python** by searching through PDF handbooks. It uses a production-grade **Retrieval-Augmented Generation (RAG)** pipeline:

1. You ask a question
2. It searches PDF handbooks using hybrid retrieval (BM25 + Vector)
3. It reranks results using FlashRank cross-encoder
4. It generates a precise, grounded answer with **exact page citations**
5. Everything runs **100% on your local machine** — no cloud, no API keys

---

## 🧰 System Requirements

Before starting, make sure you have these installed:

| Tool | Minimum Version | Download |
|:---|:---:|:---|
| 🐍 Python | 3.10+ | [python.org](https://www.python.org/downloads/) |
| 📦 Node.js | 18+ | [nodejs.org](https://nodejs.org/) |
| 🦙 Ollama | Latest | [ollama.com/download](https://ollama.com/download) |
| 🐳 Docker *(optional)* | Latest | [docker.com](https://www.docker.com/products/docker-desktop/) |

**Hardware Recommendations:**
- RAM: 8 GB minimum (16 GB recommended)
- Disk: ~4 GB free (model + embeddings)
- CPU: Any modern multi-core processor

---

## 🚀 Method 1 — One-Click Launch (Windows, Recommended)

This is the **easiest method**. Everything is handled automatically.

### Step 1: Double-click `START APP.bat` in the project root folder

```
📁 RAG-SQL-Python-Assistant\
└── 📄 START APP.bat   ← Double-click this!
```

### What happens automatically:

| Stage | Action |
|:---:|:---|
| 1️⃣ | Checks if **Ollama** is running → starts it if not |
| 2️⃣ | Checks if **llama3.2** model exists → pulls it (first-time, ~2GB) |
| 3️⃣ | Checks if **ChromaDB** embeddings exist → runs `initialize_db.py` (~38s, first-time only) |
| 4️⃣ | Starts **FastAPI backend** on `http://localhost:8000` |
| 5️⃣ | Starts **Vite frontend** on `http://localhost:5173` |
| 6️⃣ | Opens the **app in your browser** automatically |

> ✅ **Second run onward:** All checks pass instantly. Total startup takes ~15 seconds.

---

## 🧑‍💻 Method 2 — Manual Setup (All Platforms)

Use this if you're on macOS/Linux, or prefer full control.

### Step 1 — Clone the Repository

```bash
git clone https://github.com/Piyu242005/RAG-SQL-Python-Assistant.git
cd RAG-SQL-Python-Assistant
```

### Step 2 — Start Ollama

```bash
# Start the Ollama server (keep this terminal open)
ollama serve

# In a new terminal, download the language model
ollama pull llama3.2        # ~2.0 GB — first-time download only
```

> Verify Ollama is working: `curl http://localhost:11434/api/tags`

### Step 3 — Set Up the Python Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv

# Activate (choose your OS):
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# Install all Python dependencies
pip install -r requirements.txt

# Create your local config file
copy .env.example .env         # Windows
cp .env.example .env           # macOS / Linux
```

### Step 4 — Build the Vector Database *(first-time only, ~38 seconds)*

```bash
# Make sure venv is still active inside backend/
python initialize_db.py

# What this does:
# 1. Loads MySQL Handbook.pdf (71 pages → 71 chunks)
# 2. Loads The Ultimate Python Handbook.pdf (60 pages → 107 chunks)
# 3. Embeds 178 chunks using sentence-transformers/all-MiniLM-L6-v2
# 4. Saves everything to ./chroma_db (persists on disk)
```

```bash
# If you add new PDFs or want to rebuild from scratch:
python initialize_db.py --force

# For slower but higher-quality semantic chunking:
python initialize_db.py --semantic
```

### Step 5 — Start the Backend

```bash
# Inside backend/ with venv active:
python main.py

# You should see:
# ============================================================
# [*] Starting RAG System API
# [OK] Ollama setup validated
# [OK] Vector store found
# [*] API running on http://0.0.0.0:8000
# ============================================================
```

> API Docs (Swagger UI): `http://localhost:8000/docs`

### Step 6 — Set Up & Start the Frontend

```bash
# Open a new terminal:
cd frontend
npm install      # First-time only — installs React, Vite, Tailwind, etc.
npm run dev

# You should see:
# VITE v5.x ready
# ➜ Local:   http://localhost:5173/
```

> Open `http://localhost:5173` in your browser.

---

## 🐳 Method 3 — Docker (One Command)

```bash
# From the project root directory:
docker-compose up --build

# App → http://localhost
# API → http://localhost:8000
# Docs → http://localhost:8000/docs
```

> ⚠️ **Note:** Docker build pulls the llama3.2 model and builds embeddings automatically. First build takes ~10–15 minutes.

---

## ▶️ Running the App (Quick Reference)

If you've already done setup, here are the minimal commands each session:

```bash
# Terminal 1 — Ollama (skip if already running)
ollama serve

# Terminal 2 — Backend
cd backend && venv\Scripts\activate && python main.py

# Terminal 3 — Frontend
cd frontend && npm run dev
```

Then open: **http://localhost:5173**

---

## 📊 Running Evaluations

Measure retrieval accuracy and latency against a curated Q&A dataset:

```bash
cd backend
python evals/runner.py
```

**Expected output:**
```
Recall@3:        100.0%
Citation Acc:    100.0%
Avg Latency:     1.24s
```

---

## ⚙️ Configuration Reference

Edit `backend/.env` to customize behavior:

```env
# Language Model
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2             # or: mistral, llama3.1, phi3

# Embeddings (auto-downloaded from HuggingFace on first run)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Vector Store
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Chunking Strategy
CHUNK_SIZE=800                     # Characters per chunk
CHUNK_OVERLAP=150                  # Overlap between chunks

# API
API_HOST=0.0.0.0
API_PORT=8000

# CORS (add any origin that needs to access the API)
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

**Frontend env** (optional, `frontend/.env.local`):
```env
VITE_API_URL=http://localhost:8000    # Change if backend is on another host
```

---

## 🐛 Troubleshooting

### ❌ System Status shows "Not Running"

The frontend checks `/api/health` on load and auto-retries 5× every 3 seconds.  
Just wait — if you used `START APP.bat`, everything will come up automatically.

If it stays red after 30 seconds:
1. Check that `python main.py` is running in the backend terminal
2. Check that `ollama serve` is running
3. Visit `http://localhost:8000/api/health` in your browser to see the raw status

### ❌ "Failed to fetch" error in chat

- Backend is not running → start with `python main.py`
- Ollama is not running → run `ollama serve`
- ChromaDB not built → run `python initialize_db.py`

### ❌ Model not found

```bash
ollama pull llama3.2
# Alternative faster models:
ollama pull mistral      # Faster, slightly lower quality
ollama pull llama3.1     # More capable, slower
```
Update `OLLAMA_MODEL=mistral` in `backend/.env` if you switch.

### ❌ pip install fails

```bash
# Ensure Python 3.10+ and pip are up to date:
python --version          # Should be 3.10+
pip install --upgrade pip
pip install -r requirements.txt
```

### ⏳ Very slow responses

- Reduce `top_n` in `rag_pipeline.py` (reranker): `top_n=5` → `top_n=3`
- Use a smaller model: `mistral` is 2× faster than `llama3.2`
- Reduce `k` from 20 to 10 in `_initialize_retriever()`

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Code Standards

| Language | Standard |
|:---|:---|
| Python | PEP 8 + type hints + docstrings |
| JavaScript/React | Functional components + React hooks |
| Git commits | [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`) |

### Contribution Workflow

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/RAG-SQL-Python-Assistant.git

# 3. Create a feature branch
git checkout -b feat/my-feature

# 4. Make your changes and test them
#    - Test backend: python -m pytest (if tests exist)
#    - Test embedding: python initialize_db.py --force
#    - Test frontend: npm run dev

# 5. Commit your changes
git add .
git commit -m "feat: add multi-document reasoning support"

# 6. Push and open a Pull Request
git push origin feat/my-feature
# Then go to GitHub and click "Compare & Pull Request"
```

### Pull Request Checklist

- [ ] Code follows the style guidelines above
- [ ] Backend changes tested with `python main.py`
- [ ] No hardcoded API keys or secrets
- [ ] Docstrings added to new functions
- [ ] README updated if adding new features

---

## 🌐 Community Standards

This project follows the standard open-source code of conduct:

- **Be respectful** — Treat everyone with kindness and professionalism
- **Be constructive** — Focus on improvement, not criticism
- **Be inclusive** — Welcome contributors of all experience levels
- **Be patient** — This is a side project; responses may not be instant

Report issues or suggestions via [GitHub Issues](https://github.com/Piyu242005/RAG-SQL-Python-Assistant/issues).

---

## 📄 License

MIT License — free to use, modify, and distribute. See [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with 💜 by [Piyu](https://github.com/Piyu242005)**

[⭐ Star on GitHub](https://github.com/Piyu242005/RAG-SQL-Python-Assistant) · [🐛 Report a Bug](https://github.com/Piyu242005/RAG-SQL-Python-Assistant/issues) · [💡 Request a Feature](https://github.com/Piyu242005/RAG-SQL-Python-Assistant/issues)

</div>
