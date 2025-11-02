@echo off
echo ================================================
echo  Starting G-AI-TRADE System
echo ================================================
echo.

REM Get the directory where this script is located
cd /d "%~dp0"

echo [1/2] Starting Frontend (Vite)...
start "G-AI-TRADE Frontend" cmd /k "cd /d "%~dp0ui" && npm run dev"

echo [2/2] Waiting 2 seconds...
timeout /t 2 /nobreak >nul

echo [3/3] Starting Backend (Python + Uvicorn)...
start "G-AI-TRADE Backend" cmd /k "cd /d "%~dp0" && D:\git\g-ai-trade\.venv311\Scripts\python.exe -m uvicorn app.main:app --reload --log-level debug"

echo.
echo ================================================
echo  Both services are starting...
echo ================================================
echo  Frontend: http://localhost:5173
echo  Backend:  http://localhost:8000
echo  API Docs: http://localhost:8000/docs
echo ================================================
echo.
echo Press any key to close this window...
pause >nul
