#!/bin/bash

echo "=========================================="
echo "Security UI Features - Start Services"
echo "=========================================="
echo ""

if [ "$1" == "--docker" ]; then
    echo "Starting Docker services..."
    cd docker
    docker-compose up -d
    
    echo ""
    echo "Waiting for services to be ready..."
    sleep 10
    
    echo ""
    echo "=========================================="
    echo "Services are running!"
    echo "=========================================="
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
    echo "To view logs: docker-compose -f docker/docker-compose.yml logs -f"
    echo "To stop: ./stop.sh --docker"
    echo "=========================================="
else
    echo "Starting services locally..."
    
    # Check if services are already running
    if [ -f backend.pid ] && kill -0 $(cat backend.pid) 2>/dev/null; then
        echo "Backend is already running (PID: $(cat backend.pid))"
    else
        # Setup environment variables
        # Use environment variables or defaults
        DB_USER="${DB_USER:-securityuser}"
        DB_PASSWORD="${DB_PASSWORD:-}"
        DB_NAME="${DB_NAME:-securitydb}"
        DB_HOST="${DB_HOST:-localhost}"
        DB_PORT="${DB_PORT:-5432}"
        
        if [ -z "$DB_PASSWORD" ]; then
            echo "Warning: DB_PASSWORD not set. Using default connection string without password."
            export DATABASE_URL="postgresql://${DB_USER}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
        else
            export DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
        fi
        export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
        
        # Start backend
        echo "Starting backend server..."
        cd backend
        
        if [ ! -d "venv" ]; then
            echo "Error: Virtual environment not found. Please run ./build.sh first."
            exit 1
        fi
        
        source venv/bin/activate
        uvicorn app.main:app --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
        echo $BACKEND_PID > ../backend.pid
        echo "Backend started (PID: $BACKEND_PID)"
        
        cd ..
    fi
    
    if [ -f frontend.pid ] && kill -0 $(cat frontend.pid) 2>/dev/null; then
        echo "Frontend is already running (PID: $(cat frontend.pid))"
    else
        # Start frontend
        echo "Starting frontend..."
        cd frontend
        
        if [ ! -d "node_modules" ]; then
            echo "Error: node_modules not found. Please run ./build.sh first."
            exit 1
        fi
        
        REACT_APP_API_URL=http://localhost:8000 \
        REACT_APP_WS_URL=ws://localhost:8000/ws/security/events \
        PORT=3000 npm start &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > ../frontend.pid
        echo "Frontend started (PID: $FRONTEND_PID)"
        
        cd ..
    fi
    
    echo ""
    echo "Waiting for services to start..."
    sleep 5
    
    echo ""
    echo "=========================================="
    echo "Services are running!"
    echo "=========================================="
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
    if [ -f backend.pid ]; then
        echo "Backend PID: $(cat backend.pid)"
    fi
    if [ -f frontend.pid ]; then
        echo "Frontend PID: $(cat frontend.pid)"
    fi
    echo ""
    echo "To stop: ./stop.sh"
    echo "=========================================="
fi
