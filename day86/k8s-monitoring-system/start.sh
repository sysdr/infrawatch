#!/bin/bash

# Start script for K8s Monitoring System
# Uses full paths to ensure correct execution

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "========================================="
echo "Starting K8s Monitoring System"
echo "========================================="

# Check if PostgreSQL is running
if ! docker ps | grep -q k8s-monitor-postgres; then
    echo "Starting PostgreSQL..."
    docker run -d --name k8s-monitor-postgres -p 5432:5432 \
        -e POSTGRES_PASSWORD=k8s_password \
        -e POSTGRES_USER=k8s_user \
        -e POSTGRES_DB=k8s_monitor \
        postgres:16-alpine || echo "PostgreSQL may already be running"
fi

# Check if Redis is running
if ! docker ps | grep -q k8s-monitor-redis; then
    echo "Starting Redis..."
    docker run -d --name k8s-monitor-redis -p 6379:6379 \
        redis:7-alpine || echo "Redis may already be running"
fi

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 3

# Start backend
if [ -d "$BACKEND_DIR/venv" ]; then
    echo "Starting backend..."
    # Kill any existing backend process
    if [ -f "$SCRIPT_DIR/backend.pid" ]; then
        OLD_PID=$(cat "$SCRIPT_DIR/backend.pid")
        if kill -0 "$OLD_PID" 2>/dev/null; then
            echo "Stopping existing backend (PID: $OLD_PID)..."
            kill "$OLD_PID" 2>/dev/null
            sleep 2
        fi
    fi
    
    cd "$BACKEND_DIR"
    source venv/bin/activate
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    echo "Backend started (PID: $BACKEND_PID)"
    cd "$SCRIPT_DIR"
    
    # Wait a moment for backend to start
    sleep 3
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "ERROR: Backend failed to start. Check backend.log for details."
        tail -20 backend.log
        exit 1
    fi
else
    echo "ERROR: Backend virtual environment not found. Run ./build.sh first."
    exit 1
fi

# Start frontend
if [ -d "$FRONTEND_DIR/node_modules" ]; then
    echo "Starting frontend..."
    cd "$FRONTEND_DIR"
    nohup npm start > ../frontend.log 2>&1 &
    echo $! > ../frontend.pid
    echo "Frontend started (PID: $(cat ../frontend.pid))"
    cd "$SCRIPT_DIR"
else
    echo "ERROR: Frontend node_modules not found. Run npm install in frontend directory first."
    exit 1
fi

echo "========================================="
echo "Services started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "========================================="
