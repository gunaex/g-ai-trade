@echo off
REM Production Startup Script for G-AI-TRADE
REM Run this script to start the application in production mode

echo ================================
echo G-AI-TRADE Production Startup
echo ================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then run: .venv\Scripts\activate
    echo Then run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please create .env from .env.example and configure it
    echo.
    echo Press any key to continue anyway (will use defaults)...
    pause
)

REM Verify environment
echo Checking environment...
python --version
echo.

REM Check if frontend is built
if not exist "dist\index.html" (
    echo WARNING: Frontend not built!
    echo Building frontend...
    cd ui
    call npm install
    call npm run build
    cd ..
    echo Frontend built successfully!
    echo.
)

REM Initialize database if needed
if not exist "g_ai_trade.db" (
    echo Initializing database...
    python app\init_db.py
    echo.
)

REM Start the application
echo ================================
echo Starting G-AI-TRADE Server...
echo ================================
echo.
echo Server will be available at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

REM Start with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000

REM If script ends, pause
pause
