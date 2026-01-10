#!/bin/bash
set -e

echo "=== User Management API Build Script ==="

# Check if running with Docker
if [ "$1" == "docker" ]; then
    echo "Building with Docker..."
    docker-compose up -d
    echo "Waiting for services to be healthy..."
    sleep 10
    echo "Services are ready!"
    echo "Backend API: http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    exit 0
fi

# Without Docker
echo "Building without Docker (requires PostgreSQL and Redis running locally)..."

# Backend setup
cd backend
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Starting backend server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend
echo "Waiting for backend to start..."
sleep 5

# Frontend setup
cd ../frontend
echo "Installing frontend dependencies..."
npm install

echo "Starting frontend development server..."
PORT=3000 npm start &
FRONTEND_PID=$!

echo ""
echo "=== Services Started ==="
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Frontend UI: http://localhost:3000"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Run tests: cd backend && source venv/bin/activate && pytest"
echo "Stop services: ./stop.sh"
