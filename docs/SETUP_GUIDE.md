# ⚙️ Setup Guide

Follow these steps to deploy the RAG system locally.

## 1. Prerequisites
- **Python 3.10+**
- **Node.js & npm**
- **Redis:** Install and run locally (Default port `6379`).
- **Ollama:** Install from [ollama.ai](https://ollama.ai).

## 2. Prepare the AI Services

1. Start Redis:
   ```bash
   redis-server
   ```
2. Pull the required Language Model:
   ```bash
   ollama pull llama3.2
   ```

## 3. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Virtual Environment (Optional but recommended):
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   # source venv/bin/activate    # Mac/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Build the Vector Database:
   Place your PDFs in `data/pdfs/` and run:
   ```bash
   python initialize_db.py
   ```
5. Start the FastAPI server:
   ```bash
   python main.py
   ```
   *(Backend will be available at `http://localhost:8000`)*

## 4. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install packages:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *(Frontend will be available at `http://localhost:5173`)*

## 🛠️ Troubleshooting
- **Vector DB Empty Warning:** Add PDFs to `data/pdfs/` and execute `python initialize_db.py --rebuild`.
- **Redis connection refused:** The system is designed to seamlessly fall back to local in-memory dictionaries if Redis fails, but history will reset on server reboot. Ensure `redis-server` is running.
- **CORS Issues:** Make sure `VITE_API_URL` exactly matches your backend host URL in your frontend ENV configuration.
