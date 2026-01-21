#!/bin/bash
# Simple backend startup script

cd "$(dirname "$0")/backend"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found. Run ./build.sh first."
    exit 1
fi

# Activate virtual environment and start server
source venv/bin/activate
echo "Starting backend server on http://localhost:8000"
echo "Press Ctrl+C to stop"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
