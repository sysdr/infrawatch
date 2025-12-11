#!/bin/bash

set -e

PROJECT_DIR="/home/systemdr/git/infrawatch/day63/export-integration-system"

echo "=========================================="
echo "Building Export Integration System"
echo "=========================================="

# Change to project directory
cd "$PROJECT_DIR"

# Check for Docker
if command -v docker &> /dev/null; then
    echo "Building with Docker..."
    cd docker
    docker-compose up -d postgres redis
    sleep 5
    docker-compose up -d backend worker
    sleep 10
    docker-compose up -d frontend
    
    echo ""
    echo "✅ System started with Docker!"
    echo "Backend API: http://localhost:8000"
    echo "Frontend UI: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
    
else
    echo "Building without Docker..."
    
    # Backend setup
    cd "$PROJECT_DIR/backend"
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Start services
    echo "Starting Backend..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    echo "Starting Celery Worker..."
    celery -A workers.export_tasks worker --loglevel=info --concurrency=4 &
    WORKER_PID=$!
    
    # Frontend setup
    cd "$PROJECT_DIR/frontend"
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    npm start &
    FRONTEND_PID=$!
    
    echo ""
    echo "✅ System started!"
    echo "Backend API: http://localhost:8000"
    echo "Frontend UI: http://localhost:3000"
    echo ""
    echo "PIDs: Backend=$BACKEND_PID Worker=$WORKER_PID Frontend=$FRONTEND_PID"
    echo "Run ./stop.sh to stop all services"
fi

echo ""
echo "Running Tests..."
cd "$PROJECT_DIR/backend"
if [ -d "venv" ]; then
    source venv/bin/activate 2>/dev/null || true
fi
pytest tests/ -v || echo "⚠️  Tests failed or pytest not available"

echo ""
echo "=========================================="
echo "Build Complete!"
echo "=========================================="
