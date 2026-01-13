#!/bin/bash

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "================================"
echo "Building Security Assessment Platform"
echo "================================"

# Check if running with Docker
if [ "$1" == "--docker" ]; then
    echo "Building with Docker..."
    cd "$PROJECT_ROOT"
    docker-compose up --build -d
    
    echo "Waiting for services to be ready..."
    sleep 10
    
    echo "Running initial scan..."
    curl -X POST http://localhost:8000/api/security/scan/full \
        -H "Content-Type: application/json" \
        -d '{"directory": "/tmp/scan_target"}'
    
    echo ""
    echo "================================"
    echo "Services started successfully!"
    echo "Dashboard: http://localhost:3000"
    echo "API: http://localhost:8000"
    echo "================================"
else
    echo "Building without Docker..."
    
    # Backend setup
    echo "Setting up backend..."
    BACKEND_DIR="$PROJECT_ROOT/backend"
    cd "$BACKEND_DIR"
    
    # Check if venv exists, create if not
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create sample scan target
    mkdir -p /tmp/scan_target
    echo "password = 'hardcoded123'" > /tmp/scan_target/test.py
    echo "import os" >> /tmp/scan_target/test.py
    echo "os.system('rm -rf /')" >> /tmp/scan_target/test.py
    
    # Start backend
    echo "Starting backend..."
    cd "$BACKEND_DIR"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    # Wait for backend to start
    sleep 5
    
    # Frontend setup
    echo "Setting up frontend..."
    FRONTEND_DIR="$PROJECT_ROOT/frontend"
    cd "$FRONTEND_DIR"
    
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    
    # Start frontend
    echo "Starting frontend..."
    PORT=3000 npm start &
    FRONTEND_PID=$!
    
    # Wait for services
    echo "Waiting for services to start..."
    sleep 15
    
    # Run initial scan to populate dashboard
    echo "Running initial security scan..."
    sleep 5
    curl -X POST http://localhost:8000/api/security/scan/full \
        -H "Content-Type: application/json" \
        -d '{"directory": "/tmp/scan_target"}' || echo "Scan will be available after services are fully ready"
    
    echo ""
    echo "================================"
    echo "Services started successfully!"
    echo "Dashboard: http://localhost:3000"
    echo "API: http://localhost:8000"
    echo ""
    echo "Backend PID: $BACKEND_PID"
    echo "Frontend PID: $FRONTEND_PID"
    echo "================================"
    
    # Save PIDs
    cd "$PROJECT_ROOT"
    echo "$BACKEND_PID" > backend.pid
    echo "$FRONTEND_PID" > frontend.pid
fi
