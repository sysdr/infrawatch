#!/bin/bash

set -e

# Get absolute path of script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "Building Dashboard Templates System"
echo "========================================"

# Check for duplicate services
echo "Checking for duplicate services..."
if lsof -i :8000 >/dev/null 2>&1; then
    echo "WARNING: Port 8000 is already in use. Stopping existing service..."
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    sleep 2
fi

if lsof -i :3000 >/dev/null 2>&1; then
    echo "WARNING: Port 3000 is already in use. Stopping existing service..."
    pkill -f "vite" 2>/dev/null || true
    sleep 2
fi

# Backend setup
echo "Setting up backend..."
cd "$SCRIPT_DIR/backend"

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# Check for PostgreSQL (optional - will use SQLite if not available)
if command -v pg_isready >/dev/null 2>&1 && pg_isready -q 2>/dev/null; then
    echo "PostgreSQL is running..."
    # Create database
    createdb dashboard_templates 2>/dev/null || true
else
    echo "PostgreSQL not available. Using SQLite for database (tests will work)."
    # Update .env to use SQLite
    if [ -f .env ]; then
        sed -i 's|DATABASE_URL=.*|DATABASE_URL=sqlite:///./dashboard_templates.db|' .env || true
    fi
fi

# Check for Redis (optional)
if command -v redis-cli >/dev/null 2>&1 && redis-cli ping >/dev/null 2>&1; then
    echo "Redis is running..."
else
    echo "Redis not available. Continuing without Redis (caching disabled)."
fi

# Run backend
echo "Starting backend server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid

cd "$SCRIPT_DIR"

# Frontend setup
echo "Setting up frontend..."
cd "$SCRIPT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    npm install
fi

echo "Starting frontend..."
npm run dev &
FRONTEND_PID=$!
echo $FRONTEND_PID > frontend.pid

cd "$SCRIPT_DIR"

echo ""
echo "========================================"
echo "System started successfully!"
echo "========================================"
echo "Backend API: http://localhost:8000"
echo "Frontend UI: http://localhost:3000"
echo ""
echo "Run tests with: cd backend && source venv/bin/activate && pytest"
echo "Stop with: ./stop.sh"
echo ""

# Run tests
echo "Running tests..."
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
pytest tests/ -v
cd "$SCRIPT_DIR"

echo ""
echo "All tests passed! System is ready."
echo ""
