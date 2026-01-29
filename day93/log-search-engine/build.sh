#!/bin/bash

set -e

echo "========================================="
echo "Building Log Search Engine"
echo "========================================="

# Check if running with Docker
if [ "$1" == "--docker" ]; then
    echo "Building with Docker..."
    docker-compose up -d postgres redis
    
    echo "Waiting for services to be ready..."
    sleep 10
    
    docker-compose up -d backend
    sleep 5
    
    echo "Generating sample data..."
    docker-compose exec -T backend python -m app.utils.data_generator
    
    docker-compose up -d frontend
    
    echo "========================================="
    echo "Services are running!"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "========================================="
    
else
    echo "Building without Docker..."
    
    # Backend setup
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    echo "Starting PostgreSQL and Redis (ensure they are running)..."
    
    echo "Generating sample data..."
    python -m app.utils.data_generator
    
    echo "Starting backend..."
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    cd ../frontend
    echo "Installing frontend dependencies..."
    npm install
    
    echo "Starting frontend..."
    BROWSER=none npm start &
    FRONTEND_PID=$!
    
    cd ..
    
    echo "$BACKEND_PID" > backend.pid
    echo "$FRONTEND_PID" > frontend.pid
    
    echo "========================================="
    echo "Services are starting..."
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "========================================="
fi
