@echo off
echo ================================
echo  Starting G-AI-TRADE System
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Node is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/3] Starting Frontend Dev Server...
start "G-AI-TRADE Frontend" cmd /k "cd ui && npm run dev"

echo [2/3] Waiting 3 seconds...
timeout /t 3 /nobreak >nul

echo [3/3] Starting Backend API Server...
start "G-AI-TRADE Backend" cmd /k "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo ================================
echo  Services Started!
echo ================================
echo  Frontend: http://localhost:5173
echo  Backend:  http://localhost:8000
echo  API Docs: http://localhost:8000/docs
echo ================================
echo.
pause
