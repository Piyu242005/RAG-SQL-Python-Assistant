@echo off
echo [1/3] Creating environment variables...
if not exist "backend\.env" copy "backend\.env.example" "backend\.env"

echo [2/3] Setting up backend virtual environment...
cd backend
if not exist "venv" python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
cd ..

echo [3/3] Setting up frontend dependencies...
cd frontend
pip install -r requirements.txt
cd ..

echo.
echo Setup complete! You can now run the project using: powershell .\start.ps1
pause
