# ⚡ Quick Start Guide

Get Aurora up and running in under 5 minutes.

---

## Prerequisites

| Requirement | Check |
|-------------|-------|
| Python 3.8+ | `python --version` |
| Node.js 18+ | `node --version` |
| Ollama installed | [ollama.ai](https://ollama.ai) |
| PDF files in project root | `MySQL Handbook.pdf`, `The Ultimate Python Handbook.pdf` |

---

## 1 → Setup

### Automated (Recommended)

```powershell
# Windows
.\setup.bat

# Linux / macOS
chmod +x setup.sh && ./setup.sh
```

### Manual

<details>
<summary>Expand manual setup</summary>

```bash
# Ollama
ollama serve              # Terminal 1
ollama pull llama2        # Terminal 2

# Backend
cd backend
python -m venv venv
venv\Scripts\activate     # Windows (or `source venv/bin/activate`)
pip install -r requirements.txt
copy .env.example .env    # Windows (or `cp`)
python initialize_db.py

# Frontend
cd ../frontend
npm install
```

</details>

---

## 2 → Run

Open three terminals:

```bash
# Terminal 1 — Ollama (skip if it's already a service)
ollama serve
```

```bash
# Terminal 2 — Backend
cd backend
venv\Scripts\activate          # or source venv/bin/activate
python main.py
# → http://localhost:8000
```

```bash
# Terminal 3 — Frontend
cd frontend
npm install                    # first time only
npm run dev
# → http://localhost:5173
```

---

## 3 → Try It

Open **http://localhost:5173** and try these queries:

| Type | Example Query |
|------|--------------|
| 🗄️ SQL | *What are SQL JOINs and when to use each type?* |
| 🗄️ SQL | *How do I create a table in MySQL?* |
| 🐍 Python | *How do I create a Python class?* |
| 🐍 Python | *What are list comprehensions?* |

Use the **filter chips** to narrow results to a specific handbook.

---

## Common Issues

| Issue | Fix |
|-------|-----|
| Ollama not running | `ollama serve` |
| Model not found | `ollama pull llama2` |
| Vector store not initialized | `cd backend && venv\Scripts\activate && python initialize_db.py` |
| Frontend can't connect | Ensure backend is on port `8000`, check CORS/proxy config |

---

## Architecture (TL;DR)

```
User → React UI → FastAPI → RAG Pipeline → Answer + Sources
                               ↕               ↕
                           ChromaDB          Ollama
                        (vector search)    (local LLM)
```

---

**Need more detail?** See the full [README.md](README.md) and [ARCHITECTURE.md](ARCHITECTURE.md).
