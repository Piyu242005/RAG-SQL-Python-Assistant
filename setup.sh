#!/bin/bash

echo "========================================================"
echo "RAG System - Complete Setup Script (Linux/Mac)"
echo "========================================================"
echo ""

# Check Python installation
echo "[1/6] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi
echo "✓ Python is installed"
echo ""

# Check Node.js installation
echo "[2/6] Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi
echo "✓ Node.js is installed"
echo ""

# Backend setup
echo "[3/6] Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

cd ..
echo "✓ Backend setup complete"
echo ""

# Frontend setup
echo "[4/6] Setting up frontend..."
cd frontend

echo "Installing Node.js dependencies..."
npm install

cd ..
echo "✓ Frontend setup complete"
echo ""

# Check Ollama
echo "[5/6] Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "⚠️  WARNING: Ollama is not installed"
    echo "Please install Ollama from https://ollama.ai/"
    echo ""
    echo "After installing Ollama:"
    echo "  1. Run: ollama serve"
    echo "  2. Run: ollama pull llama2"
    echo "  3. Run this script again"
    exit 1
else
    echo "✓ Ollama is installed"
    echo ""
    echo "Checking if Ollama is running..."
    if ! ollama list &> /dev/null; then
        echo "⚠️  WARNING: Ollama is not running"
        echo "Please run in another terminal: ollama serve"
    else
        echo "✓ Ollama is running"
        
        echo "Checking for llama2 model..."
        if ! ollama list | grep -q "llama2"; then
            echo "Pulling llama2 model... (This may take several minutes)"
            ollama pull llama2
        else
            echo "✓ llama2 model is available"
        fi
    fi
fi
echo ""

# Initialize database
echo "[6/6] Initializing database..."
cd backend
source venv/bin/activate

echo "Running database initialization..."
python initialize_db.py

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  WARNING: Database initialization may have failed"
    echo "Please check the errors above and:"
    echo "  1. Ensure Ollama is running: ollama serve"
    echo "  2. Ensure model is pulled: ollama pull llama2"
    echo "  3. Ensure PDF files exist in the workspace root:"
    echo "     - MySQL Handbook.pdf"
    echo "     - The Ultimate Python Handbook.pdf"
    exit 1
fi

cd ..
echo ""

echo "========================================================"
echo "✅ SETUP COMPLETE!"
echo "========================================================"
echo ""
echo "To start the system:"
echo ""
echo "1. Start backend (in one terminal):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python main.py"
echo "   or: uvicorn main:app --reload"
echo ""
echo "2. Start frontend (in another terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Open browser to: http://localhost:5173"
echo ""
echo "API documentation: http://localhost:8000/docs"
echo "========================================================"
