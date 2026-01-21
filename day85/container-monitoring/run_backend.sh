#!/bin/bash

# Backend startup script - runs from correct directory

cd "$(dirname "$0")"

echo "============================================"
echo "Starting Container Monitoring Backend"
echo "============================================"
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo "Error: Please run this script from the container-monitoring directory"
    exit 1
fi

# Activate virtual environment
if [ -d "backend/venv" ]; then
    echo "Activating virtual environment..."
    source backend/venv/bin/activate
else
    echo "Creating virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
fi

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo "Installing dependencies..."
    cd backend
    pip install -r requirements.txt
    cd ..
fi

echo ""
echo "Starting backend server on http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run from container-monitoring directory so imports work
cd "$(dirname "$0")"
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
