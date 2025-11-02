@echo off
REM Helper script to start backend with correct environment
REM This is called by run.bat

echo ================================================
echo  G-AI-TRADE Backend Server
echo ================================================
echo.

cd /d "%~dp0"
echo Working Directory: %CD%
echo.

REM Use the project's virtual environment
if exist ".venv311\Scripts\python.exe" (
    echo [INFO] Using Python from .venv311
    echo [INFO] Python version:
    .venv311\Scripts\python.exe --version
    echo.
    echo [INFO] Starting uvicorn server...
    echo.
    .venv311\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
) else if exist ".venv\Scripts\python.exe" (
    echo [INFO] Using Python from .venv
    echo [INFO] Python version:
    .venv\Scripts\python.exe --version
    echo.
    echo [INFO] Starting uvicorn server...
    echo.
    .venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
) else (
    echo [WARNING] No virtual environment found!
    echo [WARNING] Using system Python - may cause dependency issues
    echo [INFO] Python version:
    python --version
    echo.
    echo [INFO] Starting uvicorn server...
    echo.
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
)

echo.
echo ================================================
echo  Server stopped
echo ================================================
pause
