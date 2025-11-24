#!/bin/bash

set -e

echo "=================================="
echo "Building Real-time UI Components"
echo "=================================="

# Check if running with Docker flag
USE_DOCKER=false
if [ "$1" == "--docker" ]; then
    USE_DOCKER=true
fi

if [ "$USE_DOCKER" == "true" ]; then
    echo "Building with Docker..."
    docker-compose build
    docker-compose up -d
    
    echo ""
    echo "Waiting for services to be ready..."
    sleep 10
    
    echo ""
    echo "=================================="
    echo "Services are running!"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "Health Check: http://localhost:8000/health"
    echo "=================================="
    
    echo ""
    echo "Running tests..."
    docker-compose exec -T backend pytest tests/ -v
    
else
    echo "Building without Docker..."
    
    # Backend setup
    echo "Setting up backend..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Start backend
    echo "Starting backend..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    
    cd ..
    
    # Frontend setup
    echo "Setting up frontend..."
    cd frontend
    npm install
    
    # Start frontend
    echo "Starting frontend..."
    npm run dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    
    cd ..
    
    echo ""
    echo "Waiting for services to be ready..."
    sleep 15
    
    echo ""
    echo "=================================="
    echo "Services are running!"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "Health Check: http://localhost:8000/health"
    echo "=================================="
    
    # Run tests
    echo ""
    echo "Running tests..."
    cd backend
    source venv/bin/activate
    PYTHONPATH=. pytest tests/ -v
    cd ..
fi

echo ""
echo "=================================="
echo "Testing API endpoints..."
echo "=================================="
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""
curl -s http://localhost:8000/api/stats | python3 -m json.tool

echo ""
echo "=================================="
echo "Setup complete!"
echo "Open http://localhost:3000 in your browser"
echo "=================================="
echo ""
echo "To stop services, run: ./stop.sh"
