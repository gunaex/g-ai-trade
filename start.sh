#!/bin/bash
echo "🚀 Starting God's Hand Trading Bot..."
python -m app.init_db
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
