@echo off
echo ========================================================
echo RAG System - Complete Setup Script (Windows)
echo ========================================================
echo.

REM Check Python installation
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
echo OK - Python is installed
echo.

REM Check Node.js installation
echo [2/6] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo OK - Node.js is installed
echo.

REM Backend setup
echo [3/6] Setting up backend...
cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install dependencies
echo Installing Python dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

REM Create .env file
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
)

cd ..
echo OK - Backend setup complete
echo.

REM Frontend setup
echo [4/6] Setting up frontend...
cd frontend

echo Installing Node.js dependencies...
call npm install

cd ..
echo OK - Frontend setup complete
echo.

REM Check Ollama
echo [5/6] Checking Ollama installation...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Ollama is not installed
    echo Please install Ollama from https://ollama.ai/
    echo.
    echo After installing Ollama:
    echo   1. Run: ollama serve
    echo   2. Run: ollama pull llama2
    echo   3. Run this script again
    pause
) else (
    echo OK - Ollama is installed
    echo.
    echo Checking if Ollama is running...
    ollama list >nul 2>&1
    if errorlevel 1 (
        echo WARNING: Ollama is not running
        echo Please run in another terminal: ollama serve
    ) else (
        echo OK - Ollama is running
        
        echo Checking for llama2 model...
        ollama list | findstr "llama2" >nul 2>&1
        if errorlevel 1 (
            echo Pulling llama2 model... (This may take several minutes)
            ollama pull llama2
        ) else (
            echo OK - llama2 model is available
        )
    )
)
echo.

REM Initialize database
echo [6/6] Initializing database...
cd backend
call venv\Scripts\activate.bat

echo Running database initialization...
python initialize_db.py

if errorlevel 1 (
    echo.
    echo WARNING: Database initialization may have failed
    echo Please check the errors above and:
    echo   1. Ensure Ollama is running: ollama serve
    echo   2. Ensure model is pulled: ollama pull llama2
    echo   3. Ensure PDF files exist in the workspace root:
    echo      - MySQL Handbook.pdf
    echo      - The Ultimate Python Handbook.pdf
    pause
)

cd ..
echo.

echo ========================================================
echo SETUP COMPLETE!
echo ========================================================
echo.
echo To start the system:
echo.
echo 1. Start backend (in one terminal):
echo    cd backend
echo    venv\Scripts\activate
echo    python main.py
echo    or: uvicorn main:app --reload
echo.
echo 2. Start frontend (in another terminal):
echo    cd frontend
echo    npm run dev
echo.
echo 3. Open browser to: http://localhost:5173
echo.
echo API documentation: http://localhost:8000/docs
echo ========================================================
pause
