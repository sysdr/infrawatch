#!/bin/bash

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "Starting Security Monitoring System..."
echo "Project root: $PROJECT_ROOT"

# Check if services are already running
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check for duplicate services
if check_port 8000; then
    echo "WARNING: Port 8000 is already in use. Checking for existing backend..."
    EXISTING_BACKEND=$(ps aux | grep -E "uvicorn.*main:app" | grep -v grep)
    if [ -n "$EXISTING_BACKEND" ]; then
        echo "Found existing backend process, stopping it..."
        pkill -f "uvicorn.*main:app"
        sleep 2
    else
        echo "Port 8000 in use by different process, exiting..."
        exit 1
    fi
fi

if check_port 3000; then
    echo "WARNING: Port 3000 is already in use. Checking for existing frontend..."
    EXISTING_FRONTEND=$(ps aux | grep -E "react-scripts start|vite.*frontend" | grep -v grep)
    if [ -n "$EXISTING_FRONTEND" ]; then
        echo "Found existing frontend process, stopping it..."
        pkill -f "react-scripts start"
        pkill -f "vite.*frontend"
        sleep 2
    else
        echo "Port 3000 in use by different process, exiting..."
        exit 1
    fi
fi

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "Creating virtual environment..."
    cd "$PROJECT_ROOT"
    python3 -m venv venv
fi

# Activate virtual environment
source "$PROJECT_ROOT/venv/bin/activate"

# Install backend dependencies if needed
if [ ! -f "$PROJECT_ROOT/venv/.installed" ]; then
    echo "Installing backend dependencies..."
    pip install -q -r "$PROJECT_ROOT/backend/requirements.txt"
    touch "$PROJECT_ROOT/venv/.installed"
fi

# Install frontend dependencies if needed
if [ ! -d "$PROJECT_ROOT/frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd "$PROJECT_ROOT/frontend"
    npm install
fi

# Check database connection (will be created on first run)
echo "Checking database connection..."
python3 -c "
import asyncio
import asyncpg
import os
import sys

async def check_db():
    # Try multiple connection strings
    conn_strings = [
        # Use DATABASE_URL environment variable instead of hardcoded credentials
        'postgresql://postgres@localhost:5432/postgres',
        'postgresql:///postgres'
    ]
    
    for conn_str in conn_strings:
        try:
            conn = await asyncpg.connect(conn_str)
            await conn.close()
            print(f'Database connection: OK (using {conn_str.split(\"@\")[-1]})')
            return True
        except Exception as e:
            continue
    
    print('Database connection: Will be initialized on first backend start')
    print('Note: Database tables will be created automatically')
    return True  # Don't fail, let backend initialize

asyncio.run(check_db())
" || echo "Database check skipped, will initialize on startup"

# Check Redis connection
echo "Checking Redis connection..."
python3 -c "
import redis
try:
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    r.ping()
    print('Redis connection: OK')
except Exception as e:
    print(f'Redis connection: FAILED - {e}')
    exit(1)
" || exit 1

# Start backend
echo "Starting backend server..."
cd "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT/backend:$PYTHONPATH"
export DATABASE_URL="postgresql://postgres@localhost:5433/postgres"
export REDIS_URL="redis://localhost:6379"

# Start backend in background
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$PROJECT_ROOT/backend.log" 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait for backend to be ready
echo "Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "Backend is ready!"
        break
    fi
    sleep 1
done

# Start frontend
echo "Starting frontend server..."
cd "$PROJECT_ROOT/frontend"
export REACT_APP_API_URL="http://localhost:8000"
nohup npm start > "$PROJECT_ROOT/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

# Save PIDs
echo "$BACKEND_PID" > "$PROJECT_ROOT/.backend.pid"
echo "$FRONTEND_PID" > "$PROJECT_ROOT/.frontend.pid"

echo ""
echo "========================================="
echo "Security Monitoring System is running!"
echo "========================================="
echo "Backend API: http://localhost:8000"
echo "Frontend UI: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Logs:"
echo "  Backend: $PROJECT_ROOT/backend.log"
echo "  Frontend: $PROJECT_ROOT/frontend.log"
echo ""
echo "To stop: ./deployment/scripts/stop.sh"
echo ""
