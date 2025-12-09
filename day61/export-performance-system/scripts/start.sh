#!/bin/bash

set -e

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Starting Export Performance System..."
echo "Project directory: $PROJECT_DIR"

# Check for duplicate backend services
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "Warning: Port 8000 is already in use. Checking if it's our backend..."
    EXISTING_PID=$(lsof -ti:8000)
    if [ -f /tmp/backend.pid ] && [ "$(cat /tmp/backend.pid)" = "$EXISTING_PID" ]; then
        echo "Backend is already running (PID: $EXISTING_PID)"
        BACKEND_PID=$EXISTING_PID
    else
        echo "Port 8000 is in use by another process (PID: $EXISTING_PID). Please stop it first."
        exit 1
    fi
else
    # Start PostgreSQL (if not running)
    # Check PostgreSQL using pg_isready if available, otherwise use docker exec or port check
    if command -v pg_isready > /dev/null 2>&1; then
        PG_CHECK="pg_isready -h localhost -p 5432"
    elif docker ps --format '{{.Names}}' | grep -q 'postgres'; then
        PG_CHECK="docker exec \$(docker ps --format '{{.Names}}' | grep postgres | head -1) pg_isready -U postgres"
    else
        PG_CHECK="timeout 2 bash -c 'cat < /dev/null > /dev/tcp/localhost/5432' 2>/dev/null"
    fi
    
    if ! eval "$PG_CHECK" > /dev/null 2>&1; then
        echo "PostgreSQL not running. Please start PostgreSQL first."
        echo "Or use Docker: $PROJECT_DIR/scripts/build.sh docker"
        exit 1
    fi

    # Start Redis (if not running)
    # Check Redis using redis-cli if available, otherwise use docker exec
    if command -v redis-cli > /dev/null 2>&1; then
        REDIS_CHECK="redis-cli ping"
    elif docker ps --format '{{.Names}}' | grep -q 'redis'; then
        REDIS_CHECK="docker exec \$(docker ps --format '{{.Names}}' | grep redis | head -1) redis-cli ping"
    else
        REDIS_CHECK="timeout 2 bash -c 'cat < /dev/null > /dev/tcp/localhost/6379' 2>/dev/null"
    fi
    
    if ! eval "$REDIS_CHECK" > /dev/null 2>&1; then
        echo "Redis not running. Please start Redis first."
        echo "Or use Docker: docker-compose up -d redis"
        exit 1
    fi

    # Start backend
    cd "$PROJECT_DIR/backend"
    if [ ! -d "venv" ]; then
        echo "Error: Backend virtual environment not found. Run build.sh first."
        exit 1
    fi
    source venv/bin/activate
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!
    cd "$PROJECT_DIR"
    
    echo "Backend started (PID: $BACKEND_PID)"
    echo $BACKEND_PID > /tmp/backend.pid
fi

# Check for duplicate frontend services
if lsof -ti:3000 > /dev/null 2>&1; then
    echo "Warning: Port 3000 is already in use. Checking if it's our frontend..."
    EXISTING_PID=$(lsof -ti:3000)
    if [ -f /tmp/frontend.pid ] && [ "$(cat /tmp/frontend.pid)" = "$EXISTING_PID" ]; then
        echo "Frontend is already running (PID: $EXISTING_PID)"
        FRONTEND_PID=$EXISTING_PID
    else
        echo "Port 3000 is in use by another process (PID: $EXISTING_PID). Please stop it first."
        exit 1
    fi
else
    # Start frontend
    cd "$PROJECT_DIR/frontend"
    if [ ! -d "node_modules" ]; then
        echo "Error: Frontend dependencies not installed. Run build.sh first."
        exit 1
    fi
    PORT=3000 npm start > /tmp/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd "$PROJECT_DIR"
    
    echo "Frontend started (PID: $FRONTEND_PID)"
    echo $FRONTEND_PID > /tmp/frontend.pid
fi

echo ""
echo "Services started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo "Metrics: http://localhost:8000/metrics"
echo ""
echo "Logs:"
echo "  Backend:  tail -f /tmp/backend.log"
echo "  Frontend: tail -f /tmp/frontend.log"
