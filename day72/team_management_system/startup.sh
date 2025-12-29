#!/bin/bash

# Team Management System Startup Script
# Checks for duplicate services, validates paths, and starts all services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "=========================================="
echo "Team Management System Startup"
echo "=========================================="

# Function to check if a process is running on a port
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to kill processes on a port
kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    if [ -n "$pids" ]; then
        echo "Killing processes on port $port: $pids"
        kill -9 $pids 2>/dev/null || true
        sleep 2
    fi
}

# Check for duplicate services
echo "Checking for duplicate services..."
PORTS=(8000 3000)
for port in "${PORTS[@]}"; do
    if check_port $port; then
        echo "WARNING: Port $port is already in use, killing existing process..."
        kill_port $port
    fi
done

# Check if PostgreSQL is running
echo "Checking PostgreSQL..."
if ! check_port 5432; then
    echo "PostgreSQL is not running on port 5432"
    echo "Starting PostgreSQL and Redis with docker-compose..."
    docker-compose up -d postgres redis
    echo "Waiting for PostgreSQL to be ready..."
    sleep 5
fi

# Check if Redis is running
echo "Checking Redis..."
if ! check_port 6379; then
    echo "Redis is not running on port 6379"
    echo "Starting Redis with docker-compose..."
    docker-compose up -d redis
    echo "Waiting for Redis to be ready..."
    sleep 3
fi

# Validate paths
echo "Validating paths..."
if [ ! -d "$BACKEND_DIR" ]; then
    echo "ERROR: Backend directory not found: $BACKEND_DIR"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    echo "ERROR: Frontend directory not found: $FRONTEND_DIR"
    exit 1
fi

if [ ! -f "$BACKEND_DIR/requirements.txt" ]; then
    echo "ERROR: Backend requirements.txt not found"
    exit 1
fi

if [ ! -f "$FRONTEND_DIR/package.json" ]; then
    echo "ERROR: Frontend package.json not found"
    exit 1
fi

# Setup backend
echo "Setting up backend..."
cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

if [ ! -f "venv/bin/activate" ]; then
    echo "ERROR: Virtual environment activation script not found"
    exit 1
fi

echo "Installing backend dependencies..."
pip install -q -r requirements.txt

# Run tests
echo "Running backend tests..."
if [ -d "tests" ] && [ -f "tests/test_teams.py" ]; then
    pytest tests/ -v --tb=short || echo "WARNING: Some tests failed"
else
    echo "WARNING: Test directory or test file not found"
fi

# Start backend
echo "Starting backend server..."
if check_port 8000; then
    echo "Port 8000 already in use, killing existing process..."
    kill_port 8000
fi

cd "$BACKEND_DIR"
uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$PROJECT_ROOT/backend.log" 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "ERROR: Backend failed to start"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

# Run demo data script
echo "Generating demo data..."
cd "$BACKEND_DIR"
source venv/bin/activate
if [ -f "demo_data.py" ]; then
    python demo_data.py || echo "WARNING: Demo data generation failed"
else
    echo "WARNING: demo_data.py not found, skipping demo data generation"
fi

# Setup frontend
echo "Setting up frontend..."
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install --prefer-offline --no-audit
fi

# Start frontend
echo "Starting frontend server (optimized for speed)..."
if check_port 3000; then
    echo "Port 3000 already in use, killing existing process..."
    kill_port 3000
fi

cd "$FRONTEND_DIR"
export HOST=0.0.0.0
export PORT=3000
export BROWSER=none
npm start > "$PROJECT_ROOT/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

# Wait for frontend to be ready
echo "Waiting for frontend to be ready..."
sleep 5

# Save PIDs to file for cleanup
echo "$BACKEND_PID" > "$PROJECT_ROOT/.backend.pid"
echo "$FRONTEND_PID" > "$PROJECT_ROOT/.frontend.pid"

echo ""
echo "=========================================="
echo "System Started Successfully!"
echo "=========================================="
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Logs:"
echo "  Backend:  $PROJECT_ROOT/backend.log"
echo "  Frontend: $PROJECT_ROOT/frontend.log"
echo ""
echo "To stop services, run: ./stop.sh"
echo "=========================================="

# Keep script running
wait


