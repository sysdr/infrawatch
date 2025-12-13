#!/bin/bash

set -e

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Building Advanced Charts Dashboard"
echo "=========================================="

# Check for duplicate services
echo "Checking for duplicate services..."
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

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

echo "Running backend tests..."
pytest tests/ -v --cov=app --cov-report=term-missing

# Start backend
echo "Starting backend server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

cd "$SCRIPT_DIR"

# Frontend setup
echo "Setting up React frontend..."
cd "$SCRIPT_DIR/frontend"

# Install dependencies
npm install

echo "Starting frontend development server..."
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

cd "$SCRIPT_DIR"

# Save PIDs for cleanup
echo $BACKEND_PID > "$SCRIPT_DIR/.backend.pid"
echo $FRONTEND_PID > "$SCRIPT_DIR/.frontend.pid"

echo ""
echo "=========================================="
echo "Build Complete!"
echo "=========================================="
echo "Backend running on: http://localhost:8000"
echo "Frontend running on: http://localhost:3000"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Testing endpoints..."
sleep 5

# Test endpoints
echo "Testing health endpoint..."
curl -s http://localhost:8000/health | python3 -m json.tool

echo ""
echo "Testing multi-series chart endpoint..."
curl -s "http://localhost:8000/api/charts/multi-series?metrics=cpu&metrics=memory" | python3 -m json.tool | head -20

echo ""
echo "=========================================="
echo "All services running successfully!"
echo "Press Ctrl+C and run ./stop.sh to stop"
echo "=========================================="

# Keep script running
wait
