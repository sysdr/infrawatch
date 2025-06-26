#!/bin/bash
echo "🚀 Starting Password Security Demo"
echo "=================================="

# Start Redis if not running
if ! pgrep -f redis-server > /dev/null; then
    echo "Starting Redis server..."
    redis-server --daemonize yes --appendonly yes
    sleep 2
fi

# Install dependencies
pip install -r requirements.txt

# Run the application
echo "Starting FastAPI application..."
echo "Visit http://localhost:8000 to see the demo"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
