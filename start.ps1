# start.ps1
# This script starts both the FastAPI backend and the Streamlit frontend.

$BackendDir = "backend"
$FrontendDir = "frontend"

echo "🚀 Starting RAG Assistant..."

# 1. Start Backend in a new window
echo "Starting Backend (FastAPI)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $BackendDir; .\venv\Scripts\activate; uvicorn main:app --reload --port 8000"

# Wait a few seconds for backend to warm up
Start-Sleep -Seconds 3

# 2. Start Frontend
echo "Starting Frontend (Streamlit)..."
cd $FrontendDir
python -m streamlit run app.py
