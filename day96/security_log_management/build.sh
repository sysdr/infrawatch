#!/bin/bash

echo "=================================="
echo "Security Log Management System"
echo "Build and Run Script"
echo "=================================="
echo ""

# Use script directory as project root (support full-path execution)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if running with Docker
if [ "$1" == "--docker" ]; then
    echo "Building with Docker..."
    cd "$SCRIPT_DIR/docker"
    docker-compose up --build -d
    echo ""
    echo "Services started with Docker!"
    echo "Backend API: http://localhost:8000"
    echo "Frontend UI: http://localhost:3000"
    echo ""
    echo "Run './stop.sh --docker' to stop services"
    exit 0
fi

# Local setup
echo "Setting up local environment..."

# Backend setup
echo "Setting up backend..."
cd "$SCRIPT_DIR/backend"

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# Start PostgreSQL and Redis (assuming they're installed locally)
echo "Ensure PostgreSQL and Redis are running locally"
echo "PostgreSQL: postgresql://postgres:postgres@localhost:5432/security_logs"
echo "Redis: redis://localhost:6379/0"

# Create database if it doesn't exist
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/security_logs"
export REDIS_URL="redis://localhost:6379/0"

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

cd "$SCRIPT_DIR"

# Frontend setup
echo "Setting up frontend..."
cd "$SCRIPT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    npm install
fi

# Start frontend
PORT=3000 npm start &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"

cd ..

# Save PIDs to project root
echo $BACKEND_PID > "$SCRIPT_DIR/.backend.pid"
echo $FRONTEND_PID > "$SCRIPT_DIR/.frontend.pid"

echo ""
echo "=================================="
echo "Build Complete!"
echo "=================================="
echo ""
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Frontend UI: http://localhost:3000"
echo ""
echo "Run tests: cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/ -v"
echo "Seed demo data (for non-zero dashboard): ./seed_demo.sh"
echo "Stop services: ./stop.sh"
echo ""
