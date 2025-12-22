#!/bin/bash

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================="
echo "Building Dashboard Integration Testing System"
echo "Working directory: $SCRIPT_DIR"
echo "=================================="

# Check for duplicate services
echo "Checking for existing services..."
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo "WARNING: Backend service already running. Stopping existing instances..."
    pkill -f "uvicorn app.main:app" || true
    sleep 2
fi

if pgrep -f "vite" > /dev/null; then
    echo "WARNING: Frontend service already running. Stopping existing instances..."
    pkill -f "vite" || true
    sleep 2
fi

# Backend setup
echo "Setting up Python backend..."
cd "$SCRIPT_DIR/backend"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo "Backend dependencies installed!"

# Frontend setup
echo "Setting up React frontend..."
cd "$SCRIPT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    npm install
else
    echo "Frontend dependencies already installed, skipping..."
fi

echo "Frontend dependencies ready!"

# Start services
echo "=================================="
echo "Starting services..."
echo "=================================="

# Start Redis (if not running)
if ! pgrep -x "redis-server" > /dev/null; then
    echo "Starting Redis..."
    redis-server --daemonize yes || echo "Redis may already be running or not installed"
    sleep 1
fi

# Start backend
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
echo "Starting FastAPI backend on port 8000..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
sleep 5

# Verify backend is running
if ! pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo "ERROR: Backend failed to start. Check /tmp/backend.log"
    cat /tmp/backend.log
    exit 1
fi

# Start frontend
cd "$SCRIPT_DIR/frontend"
echo "Starting React frontend on port 3000..."
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"
sleep 8

# Verify frontend is running
if ! pgrep -f "vite" > /dev/null; then
    echo "ERROR: Frontend failed to start. Check /tmp/frontend.log"
    cat /tmp/frontend.log
    exit 1
fi

echo "=================================="
echo "Running Tests..."
echo "=================================="

# Wait a bit more for services to be fully ready
sleep 3

# Run integration tests
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
echo "Running integration tests..."
pytest tests/integration/ -v || echo "WARNING: Some integration tests failed"

# Run performance tests (short duration)
echo "Running performance tests (30 seconds)..."
cd "$SCRIPT_DIR/tests"
if command -v locust &> /dev/null; then
    locust -f performance_test.py --headless --users 10 --spawn-rate 2 --run-time 30s --host http://localhost:8000 || echo "WARNING: Performance tests had issues"
else
    echo "WARNING: locust not installed, skipping performance tests"
fi

echo "=================================="
echo "Dashboard Integration Testing System is running!"
echo "=================================="
echo "Backend API: http://localhost:8000"
echo "Frontend Dashboard: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Testing the system:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Watch real-time metrics streaming"
echo "3. Try different load levels (Normal/High/Burst)"
echo "4. Observe performance stats updating"
echo ""
echo "To stop services, run: $SCRIPT_DIR/stop.sh"
echo "Or press Ctrl+C"
echo "=================================="

# Wait for user interruption
trap "echo 'Stopping services...'; pkill -P $$; exit" INT TERM
wait
