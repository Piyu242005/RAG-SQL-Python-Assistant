# ⚙️ Setup & Installation Guide

> **Follow these steps to get Piyu AI Assistant running on your local machine or in production.**

---

## 🛠️ Local Installation

### 1. Prerequisites
Ensure you have the following installed:
- [Python 3.10+](https://www.python.org/)
- [Node.js 18+](https://nodejs.org/)
- [Ollama](https://ollama.ai/)
- [Redis](https://redis.io/docs/install/install-redis/) (Optional for local, required for Docker)

### 2. Ollama Configuration
1. Start the Ollama server:
   ```bash
   ollama serve
   ```
2. Pull the required model:
   ```bash
   ollama pull llama3.2
   ```

### 3. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Unix/macOS
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment:
   - Rename `.env.example` to `.env`.
   - Update `API_KEY` and `REDIS_URL` if needed.

### 4. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

---

## 🐳 Docker Deployment (Recommended)

To run the entire stack (Redis, Backend, Frontend) with one command:

```bash
docker-compose up --build
```

**Note:** Ensure Ollama is running on your host machine and accessible at `http://host.docker.internal:11434`.

---

## 🔧 Troubleshooting

### ❌ Backend can't connect to Ollama
- **Fix**: Ensure `ollama serve` is running.
- **Check**: Run `curl http://localhost:11434/api/tags`. If it fails, Ollama is not running.

### ❌ No documents found / Empty answers
- **Fix**: You must initialize the vector database.
- **Run**: `python initialize_db.py` in the `backend` folder.

### ❌ Frontend shows "401 Unauthorized"
- **Fix**: Ensure the `API_KEY` in `backend/.env` matches the key in `frontend/src/services/api.js`.

### ❌ Redis connection errors
- **Fix**: If running locally without Docker, ensure Redis server is started (`redis-server`). If you don't want Redis, the system will fall back to in-memory history automatically.

---

## 🚀 Production Optimization Tips
1. **GPU Acceleration**: If you have an NVIDIA GPU, ensure Ollama is using CUDA for significantly faster inference.
2. **Persistence**: Back up the `backend/chroma_db` directory to avoid re-indexing documents.
3. **Caching**: Increase the Redis cache expiration time in `rag_pipeline.py` for more aggressive caching of common queries.
