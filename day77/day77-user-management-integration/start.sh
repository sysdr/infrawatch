#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "Starting User Management Integration Services"
echo "========================================"

# Check if services are already running
BACKEND_RUNNING=false
FRONTEND_RUNNING=false

if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "✓ Backend is already running on http://localhost:8000"
    BACKEND_RUNNING=true
fi

if curl -s http://localhost:3000 >/dev/null 2>&1; then
    echo "✓ Frontend is already running on http://localhost:3000"
    FRONTEND_RUNNING=true
fi

if [ "$BACKEND_RUNNING" = true ] && [ "$FRONTEND_RUNNING" = true ]; then
    echo ""
    echo "========================================"
    echo "✓ All services are already running!"
    echo "========================================"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
    curl -s http://localhost:8000/api/tests/status | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'Dashboard Metrics: Users={d[\"users\"]}, Teams={d[\"teams\"]}, Permissions={d[\"permissions\"]}')" 2>/dev/null || echo ""
    exit 0
fi

# Start Backend if not running
if [ "$BACKEND_RUNNING" = false ]; then
    echo "Starting backend..."
    cd "$SCRIPT_DIR/backend"

    if [ ! -d "venv" ] || [ ! -f "venv/bin/activate" ]; then
        echo "Creating virtual environment..."
        rm -rf venv
        python3 -m venv venv
    fi

    if [ -f "$SCRIPT_DIR/backend/venv/bin/activate" ]; then
        source "$SCRIPT_DIR/backend/venv/bin/activate"
    else
        echo "Error: Virtual environment activation script not found"
        exit 1
    fi

    # Install dependencies if needed
    if ! python -c "import fastapi" 2>/dev/null; then
        echo "Installing backend dependencies..."
        pip install --upgrade pip
        pip install -r requirements.txt
    fi

    # Start backend
    echo "Starting backend server on port 8000..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$SCRIPT_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$SCRIPT_DIR/backend/backend.pid"
    echo "Backend started with PID: $BACKEND_PID"

    # Wait for backend to be ready
    echo "Waiting for backend to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            echo "✓ Backend is ready!"
            break
        fi
        sleep 1
    done
fi

# Start Frontend if not running
if [ "$FRONTEND_RUNNING" = false ]; then
    echo "Starting frontend..."
    cd "$SCRIPT_DIR/frontend"

    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi

    # Fix permissions for react-scripts
    if [ -f "node_modules/.bin/react-scripts" ]; then
        chmod +x node_modules/.bin/react-scripts
    fi

    echo "Starting frontend server on port 3000..."
    BROWSER=none npm start > "$SCRIPT_DIR/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$SCRIPT_DIR/frontend/frontend.pid"
    echo "Frontend started with PID: $FRONTEND_PID"
fi

echo ""
echo "========================================"
echo "✓ Services Started!"
echo "========================================"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
if [ "$BACKEND_RUNNING" = false ]; then
    echo "Backend PID: $BACKEND_PID"
fi
if [ "$FRONTEND_RUNNING" = false ]; then
    echo "Frontend PID: $FRONTEND_PID"
fi
echo ""
echo "Logs:"
echo "  Backend: $SCRIPT_DIR/backend.log"
echo "  Frontend: $SCRIPT_DIR/frontend.log"
echo ""
echo "Note: Frontend may take 1-2 minutes to fully start"
echo "========================================"
