#!/bin/bash

set -e

echo "=========================================="
echo "Building Day 51: Real-time Data Streaming"
echo "=========================================="

# Check if Docker mode
if [ "$1" == "--docker" ]; then
    echo "Building with Docker..."
    docker-compose build
    echo "Starting services..."
    docker-compose up -d
    
    echo ""
    echo "Waiting for services to start..."
    sleep 10
    
    echo "Services started successfully!"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo ""
    echo "Run 'docker-compose logs -f' to see logs"
    echo "Run './stop.sh --docker' to stop services"
    
else
    echo "Building without Docker..."
    
    # Backend setup
    echo ""
    echo "Setting up backend..."
    cd backend
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -r requirements.txt
    
    echo "Running backend tests..."
    pytest tests/ -v
    
    echo "Starting backend server..."
    python -m uvicorn app.main:socket_app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    
    cd ..
    
    # Frontend setup
    echo ""
    echo "Setting up frontend..."
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    
    echo "Starting frontend server..."
    npm run dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    
    cd ..
    
    echo ""
    echo "Waiting for services to start..."
    sleep 10
    
    echo ""
    echo "=========================================="
    echo "Build Complete!"
    echo "=========================================="
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
    echo "Testing connection..."
    curl -s http://localhost:8000/health | python3 -m json.tool
    
    echo ""
    echo "=========================================="
    echo "Demo Instructions:"
    echo "=========================================="
    echo "1. Open http://localhost:3000 in your browser"
    echo "2. Watch metrics streaming in real-time"
    echo "3. Monitor connection status indicator"
    echo "4. Check streaming statistics panel"
    echo ""
    echo "To stop: ./stop.sh"
fi
