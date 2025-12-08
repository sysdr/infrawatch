#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Building Advanced Analytics System ==="

# Check for duplicate services
echo "Checking for existing services..."
if pgrep -f "uvicorn.*app.main" > /dev/null; then
    echo "⚠️  Backend service already running. Stopping existing instance..."
    pkill -f "uvicorn.*app.main"
    sleep 2
fi

if pgrep -f "react-scripts.*start" > /dev/null; then
    echo "⚠️  Frontend service already running. Stopping existing instance..."
    pkill -f "react-scripts.*start"
    sleep 2
fi

# Backend setup
echo "Setting up backend..."
if [ ! -d "backend" ]; then
    echo "❌ ERROR: backend directory not found!"
    exit 1
fi

cd "$SCRIPT_DIR/backend"

if [ ! -f "requirements.txt" ]; then
    echo "❌ ERROR: backend/requirements.txt not found!"
    exit 1
fi

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

if [ ! -f "app/main.py" ]; then
    echo "❌ ERROR: backend/app/main.py not found!"
    exit 1
fi

echo "Starting backend server..."
cd "$SCRIPT_DIR/backend"
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd "$SCRIPT_DIR"
sleep 5

# Verify backend is running
if ! pgrep -f "uvicorn.*app.main" > /dev/null; then
    echo "❌ ERROR: Backend failed to start!"
    exit 1
fi

# Frontend setup
echo "Setting up frontend..."
cd "$SCRIPT_DIR/frontend"

if [ ! -f "package.json" ]; then
    echo "❌ ERROR: frontend/package.json not found!"
    exit 1
fi

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ ERROR: Frontend dependencies installation failed!"
        exit 1
    fi
fi

echo "Starting frontend server..."
npm start &
FRONTEND_PID=$!
sleep 15

# Verify frontend is running
if ! pgrep -f "react-scripts.*start" > /dev/null; then
    echo "❌ ERROR: Frontend failed to start!"
    exit 1
fi

echo ""
echo "=== System Running ==="
echo "Backend API: http://localhost:8000"
echo "Frontend Dashboard: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"

wait
