#!/bin/bash

set -e

echo "========================================"
echo "Building WebSocket Infrastructure"
echo "========================================"

# Detect OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    IS_WINDOWS=true
else
    IS_WINDOWS=false
fi

# Check if Docker is requested
if [ "$1" == "docker" ]; then
    echo "Building and running with Docker..."
    docker-compose up --build -d
    
    echo ""
    echo "✅ Services started with Docker!"
    echo "Backend: http://localhost:5000"
    echo "Frontend: http://localhost:3000"
    echo ""
    echo "View logs: docker-compose logs -f"
    echo "Stop services: docker-compose down"
    exit 0
fi

# Non-Docker build
echo "Building without Docker..."

# Setup Python backend
echo "Setting up Python backend..."
cd backend

if [ "$IS_WINDOWS" = true ]; then
    python -m venv venv
    ./venv/Scripts/activate
else
    python3 -m venv venv
    source venv/bin/activate
fi

pip install --upgrade pip
pip install -r requirements.txt

echo "Running backend tests..."
pytest tests/ -v

echo "Starting backend server..."
if [ "$IS_WINDOWS" = true ]; then
    start python src/server.py
else
    python src/server.py &
fi
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID" > ../backend.pid

cd ..

# Setup React frontend
echo "Setting up React frontend..."
cd frontend

if command -v npm &> /dev/null; then
    npm install
    
    echo "Starting frontend..."
    if [ "$IS_WINDOWS" = true ]; then
        start npm start
    else
        npm start &
    fi
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID" > ../frontend.pid
else
    echo "❌ npm not found. Please install Node.js"
    exit 1
fi

cd ..

echo ""
echo "✅ Build complete!"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo ""
echo "To stop: ./stop.sh"
