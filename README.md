# RAG System - SQL & Python Documentation Assistant

A production-ready Retrieval-Augmented Generation (RAG) system that provides intelligent question-answering for SQL (MySQL) and Python programming using local PDF handbooks. Built with React, FastAPI, LangChain, and Ollama.

## 🌟 Features

- **Intelligent Q&A**: Ask questions about SQL or Python and get accurate answers with source citations
- **Local LLM**: Uses Ollama for completely free, privacy-focused AI responses
- **Document Filtering**: Filter searches to specific documentation (MySQL only, Python only, or both)
- **Source Attribution**: Every answer includes references to the source PDF and page numbers
- **Modern UI**: Clean, responsive chat interface built with React and Tailwind CSS
- **Production-Ready**: FastAPI backend with proper error handling and validation
- **Semantic Search**: ChromaDB vector store with HuggingFace embeddings for accurate retrieval

## 📋 Prerequisites

- **Python 3.8+** - [Download](https://www.python.org/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Ollama** - [Download](https://ollama.ai/)
- **PDF Documents**:
  - MySQL Handbook.pdf
  - The Ultimate Python Handbook.pdf
  
  *(Place these files in the workspace root directory)*

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

The setup script will:
1. ✅ Check Python and Node.js installations
2. ✅ Set up Python virtual environment and install dependencies
3. ✅ Install Node.js dependencies
4. ✅ Check and configure Ollama
5. ✅ Process PDFs and create vector store
6. ✅ Validate the system

### Option 2: Manual Setup

#### 1. Install Ollama and Pull Model

```bash
# Start Ollama service
ollama serve

# In another terminal, pull the model
ollama pull llama2
# or for better performance: ollama pull mistral
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env  # Windows
# or
cp .env.example .env    # Linux/Mac

# Initialize database (process PDFs and create vector store)
python initialize_db.py
```

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

## 🎯 Running the Application

### Terminal 1: Start Backend

```bash
cd backend
# Activate virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Start FastAPI server
python main.py
# or
uvicorn main:app --reload
```

Backend will be available at: http://localhost:8000

API Documentation: http://localhost:8000/docs

### Terminal 2: Start Frontend

```bash
cd frontend

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:5173

### Terminal 3: Ollama (if not running as service)

```bash
ollama serve
```

## 📁 Project Structure

```
RAG System/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── document_processor.py  # PDF extraction and chunking
│   ├── vector_store.py         # ChromaDB vector store management
│   ├── llm_config.py           # Ollama LLM configuration
│   ├── rag_pipeline.py         # RAG chain implementation
│   ├── models.py               # Pydantic models for validation
│   ├── initialize_db.py        # Database initialization script
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment variables template
│   └── routers/
│       ├── __init__.py
│       └── chat.py             # Chat API endpoints
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatContainer.jsx   # Main chat layout
│   │   │   ├── ChatMessage.jsx     # Message display
│   │   │   ├── ChatInput.jsx       # User input
│   │   │   └── SourceCard.jsx      # Source citations
│   │   ├── hooks/
│   │   │   └── useChat.js          # Chat state management
│   │   ├── services/
│   │   │   └── api.js              # API client
│   │   ├── App.jsx                 # Main app component
│   │   ├── main.jsx                # React entry point
│   │   └── index.css               # Global styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── MySQL Handbook.pdf          # SQL knowledge base
├── The Ultimate Python Handbook.pdf  # Python knowledge base
├── setup.bat                   # Windows setup script
├── setup.sh                    # Linux/Mac setup script
└── README.md                   # This file
```

## 🔧 Configuration

### Backend Configuration (`.env` file)

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2  # or mistral, llama3, etc.

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Vector Store
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

### Frontend Configuration

Edit `frontend/src/services/api.js` to change the API base URL if needed:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

## 🔍 API Endpoints

### POST `/api/chat`
Send a query to the RAG system.

**Request:**
```json
{
  "query": "What is a SQL JOIN?",
  "doc_type": "mysql"  // optional: "mysql" or "python"
}
```

**Response:**
```json
{
  "answer": "A SQL JOIN clause...",
  "sources": [
    {
      "source": "MySQL Handbook.pdf",
      "page": 42,
      "doc_type": "mysql",
      "content_preview": "..."
    }
  ],
  "success": true
}
```

### GET `/api/health`
Check system health status.

### GET `/api/documents`
Get statistics about indexed documents.

### POST `/api/initialize`
Reinitialize the system (reprocess PDFs).

## 🧪 Testing

### Test Backend

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Test document processing
python document_processor.py

# Test vector store
python vector_store.py

# Test Ollama connection
python llm_config.py

# Test RAG pipeline
python rag_pipeline.py
```

### Test Frontend

```bash
cd frontend
npm run dev
```

Open http://localhost:5173 and try sample queries:
- "What are SQL JOINs?"
- "How do I create a Python class?"
- "Explain SELECT statement in SQL"

## 🐛 Troubleshooting

### Issue: "Ollama is not running"

**Solution:**
```bash
# Start Ollama in a separate terminal
ollama serve
```

### Issue: "Model not found"

**Solution:**
```bash
# Pull the required model
ollama pull llama2
# or
ollama pull mistral
```

### Issue: "No PDF files found"

**Solution:**
- Ensure `MySQL Handbook.pdf` and `The Ultimate Python Handbook.pdf` are in the workspace root directory
- Run `python backend/initialize_db.py` to reprocess documents

### Issue: "Vector store not initialized"

**Solution:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python initialize_db.py
```

### Issue: "Frontend can't connect to backend"

**Solution:**
- Ensure backend is running on port 8000
- Check CORS settings in `backend/config.py`
- Verify proxy settings in `frontend/vite.config.js`

### Issue: "Slow responses"

**Solutions:**
- Use a smaller model: `ollama pull mistral` (faster than llama2)
- Reduce `k` parameter in `backend/rag_pipeline.py` (retrieve fewer documents)
- Increase `CHUNK_SIZE` in `.env` (fewer, larger chunks)

## 📊 Performance

- **Document Processing**: ~2-5 minutes for both PDFs (one-time)
- **Embedding Generation**: ~3-8 minutes (one-time)
- **Query Response Time**: 5-15 seconds (depends on model and hardware)
- **Memory Usage**: ~2-4 GB RAM (with llama2)

## 🔒 Privacy & Security

- **100% Local**: All processing happens on your machine
- **No API Costs**: Uses free, open-source Ollama models
- **No Data Sent**: Your documents and queries never leave your computer
- **No API Keys**: No registration or API keys required

## 🚢 Deployment

### Production Build

**Backend:**
```bash
cd backend
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

**Frontend:**
```bash
cd frontend
npm run build
# Serve the 'dist' folder with any static file server
```

### Docker (Optional)

Create `Dockerfile` for backend and frontend, then:
```bash
docker-compose up
```

## 🤝 Contributing

This is a standalone RAG system. To customize:

1. **Add More PDFs**: Update `backend/document_processor.py` to process additional documents
2. **Change Models**: Edit `OLLAMA_MODEL` in `.env` file
3. **Customize UI**: Modify React components in `frontend/src/components/`
4. **Adjust Chunking**: Change `CHUNK_SIZE` and `CHUNK_OVERLAP` in `.env`

## 📝 License

This project is provided as-is for educational and personal use.

## 🙏 Acknowledgments

- **LangChain**: RAG framework
- **Ollama**: Local LLM runtime
- **ChromaDB**: Vector database
- **FastAPI**: Backend framework
- **React**: Frontend framework
- **Tailwind CSS**: Styling

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Ollama documentation: https://ollama.ai/
3. Check LangChain docs: https://python.langchain.com/

---

**Enjoy your local RAG system! 🚀**
