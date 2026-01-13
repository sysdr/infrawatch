#!/bin/bash

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "================================"
echo "Starting Security Assessment Platform"
echo "================================"

# Check if backend is already running
if lsof -i :8000 >/dev/null 2>&1; then
    echo "Backend already running on port 8000"
    BACKEND_RUNNING=true
else
    BACKEND_RUNNING=false
fi

# Check if frontend is already running
if lsof -i :3000 >/dev/null 2>&1; then
    echo "Frontend already running on port 3000"
    FRONTEND_RUNNING=true
else
    FRONTEND_RUNNING=false
fi

# Start backend if not running
if [ "$BACKEND_RUNNING" = false ]; then
    echo "Starting backend..."
    cd "$BACKEND_DIR"
    
    # Check if venv exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # Check if dependencies are installed
    if ! python3 -c "import fastapi" 2>/dev/null; then
        echo "Installing backend dependencies..."
        pip install -r requirements.txt >/dev/null 2>&1
    fi
    
    # Create scan target directory if it doesn't exist
    mkdir -p /tmp/scan_target
    if [ ! -f /tmp/scan_target/test.py ]; then
        echo "password = 'hardcoded123'" > /tmp/scan_target/test.py
        echo "import os" >> /tmp/scan_target/test.py
        echo "eval('os.system')" >> /tmp/scan_target/test.py
    fi
    
    # Start backend
    cd "$BACKEND_DIR"
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "$BACKEND_PID" > "$PROJECT_ROOT/backend.pid"
    echo "Backend started (PID: $BACKEND_PID)"
    
    # Wait for backend to be ready
    echo "Waiting for backend to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            echo "Backend is ready!"
            break
        fi
        sleep 1
    done
else
    echo "Using existing backend service"
fi

# Start frontend if not running
if [ "$FRONTEND_RUNNING" = false ]; then
    echo "Starting frontend..."
    cd "$FRONTEND_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install >/dev/null 2>&1
    fi
    
    # Start frontend
    cd "$FRONTEND_DIR"
    PORT=3000 nohup npm start > /tmp/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "$FRONTEND_PID" > "$PROJECT_ROOT/frontend.pid"
    echo "Frontend started (PID: $FRONTEND_PID)"
    echo "Frontend is compiling, it will be available at http://localhost:3000 shortly..."
else
    echo "Using existing frontend service"
fi

# Run initial scan if backend just started
if [ "$BACKEND_RUNNING" = false ]; then
    echo ""
    echo "Running initial security scan to populate dashboard..."
    sleep 3
    curl -X POST http://localhost:8000/api/security/scan/full \
        -H "Content-Type: application/json" \
        -d '{"directory": "/tmp/scan_target"}' >/dev/null 2>&1 || echo "Scan will be available after services are fully ready"
fi

echo ""
echo "================================"
echo "Services Status:"
echo "================================"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
if [ -f "$PROJECT_ROOT/backend.pid" ]; then
    echo "Backend PID: $(cat $PROJECT_ROOT/backend.pid)"
fi
if [ -f "$PROJECT_ROOT/frontend.pid" ]; then
    echo "Frontend PID: $(cat $PROJECT_ROOT/frontend.pid)"
fi
echo "================================"
