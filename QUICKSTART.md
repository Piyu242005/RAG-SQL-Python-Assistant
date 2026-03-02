# 🚀 Quick Start Guide

## Prerequisites Check

✅ Python 3.8+ installed
✅ Node.js 18+ installed  
✅ Ollama installed
✅ PDF files in workspace root:
   - MySQL Handbook.pdf
   - The Ultimate Python Handbook.pdf

## Setup (5 minutes)

### Windows

```powershell
# Run automated setup
.\setup.bat
```

### Linux/Mac

```bash
# Make executable and run
chmod +x setup.sh
./setup.sh
```

## Running the System

### 1. Start Ollama (if not running)

```bash
ollama serve
```

### 2. Start Backend

Open Terminal 1:

```bash
cd backend

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Start server
python main.py
```

➡️ Backend ready at: http://localhost:8000

### 3. Start Frontend

Open Terminal 2:

```bash
cd frontend
npm run dev
```

➡️ Frontend ready at: http://localhost:5173

## Test It Out

Open http://localhost:5173 in your browser and try:

**SQL Questions:**
- "What is a SQL JOIN?"
- "How do I create a table in MySQL?"
- "Explain the SELECT statement"

**Python Questions:**
- "How do I create a Python class?"
- "What are list comprehensions?"
- "Explain Python decorators"

## Common Issues

### "Ollama not running"
```bash
ollama serve
```

### "Model not found"
```bash
ollama pull llama2
```

### "Vector store not initialized"
```bash
cd backend
venv\Scripts\activate  # or source venv/bin/activate
python initialize_db.py
```

## Architecture

```
User Query → React UI → FastAPI Backend → RAG Pipeline
                                         ↓
                         Vector Search (ChromaDB) + LLM (Ollama)
                                         ↓
                         Answer + Source Citations → User
```

## Key Files

- `backend/main.py` - API server
- `backend/rag_pipeline.py` - RAG logic
- `frontend/src/App.jsx` - UI entry point
- `README.md` - Full documentation

---

**Need help?** Check the full README.md for detailed troubleshooting.
