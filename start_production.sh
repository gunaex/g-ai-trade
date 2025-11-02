#!/bin/bash
# Production Startup Script for G-AI-TRADE
# Run this script to start the application in production mode

echo "================================"
echo "G-AI-TRADE Production Startup"
echo "================================"
echo

# Check if virtual environment exists
if [ ! -f ".venv/bin/activate" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run: python -m venv .venv"
    echo "Then run: source .venv/bin/activate"
    echo "Then run: pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Please create .env from .env.example and configure it"
    echo
    echo "Press Enter to continue anyway (will use defaults)..."
    read
fi

# Verify environment
echo "Checking environment..."
python --version
echo

# Check if frontend is built
if [ ! -f "dist/index.html" ]; then
    echo "WARNING: Frontend not built!"
    echo "Building frontend..."
    cd ui
    npm install
    npm run build
    cd ..
    echo "Frontend built successfully!"
    echo
fi

# Initialize database if needed
if [ ! -f "g_ai_trade.db" ]; then
    echo "Initializing database..."
    python app/init_db.py
    echo
fi

# Start the application
echo "================================"
echo "Starting G-AI-TRADE Server..."
echo "================================"
echo
echo "Server will be available at: http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo

# Start with uvicorn
# For production, use gunicorn with uvicorn workers:
# gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

uvicorn app.main:app --host 0.0.0.0 --port 8000
