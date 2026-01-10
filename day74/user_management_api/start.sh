#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== User Management API Startup Script ==="
echo ""

# Quick check for PostgreSQL and Redis (start Docker services if needed, but don't wait)
echo "Checking database services..."
if ! PGPASSWORD=postgres psql -h localhost -U postgres -d usermgmt -c "SELECT 1;" >/dev/null 2>&1; then
    if [ -f "docker-compose.yml" ]; then
        echo "Starting PostgreSQL and Redis with Docker..."
        docker-compose up -d postgres redis 2>/dev/null || true
        # Create database if needed (non-blocking, in background)
        (sleep 3 && PGPASSWORD=postgres psql -h localhost -U postgres -c "CREATE DATABASE usermgmt;" 2>/dev/null || true) &
    fi
fi

if ! redis-cli -h localhost ping >/dev/null 2>&1; then
    if [ -f "docker-compose.yml" ]; then
        docker-compose up -d redis 2>/dev/null || true
    fi
fi
echo ""

# Check for duplicate services (kill without sleep delays)
echo "Checking for existing services..."
lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti:3000 2>/dev/null | xargs kill -9 2>/dev/null || true
echo ""

# Backend setup
echo "Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
VENV_PYTHON="$(pwd)/venv/bin/python"

# Only check if dependencies need installation (skip if already installed)
if ! $VENV_PYTHON -c "import fastapi" 2>/dev/null; then
    echo "Installing backend dependencies..."
    $VENV_PYTHON -m pip install --upgrade pip --quiet
    $VENV_PYTHON -m pip install -r requirements.txt --quiet
else
    echo "Backend dependencies already installed."
fi

# Skip database seeding to save time (can be run manually if needed)
# echo "Seeding database with demo data..."
# if [ -f "scripts/seed_data.py" ]; then
#     PYTHONPATH=. $VENV_PYTHON scripts/seed_data.py 2>/dev/null || true
# fi

# Start backend
echo "Starting backend server on port 8000..."
PYTHONPATH=. $VENV_PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port 8000 >../backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID (starting in background)"
echo ""

# Frontend setup
cd ../frontend
echo "Setting up frontend..."

# Check if build exists, if not build it
if [ ! -d "build" ] || [ ! -f "build/index.html" ]; then
    echo "Building frontend (this may take a minute)..."
    if [ ! -d "node_modules" ]; then
        npm install --silent >/dev/null 2>&1
    fi
    npm run build --silent >../frontend-build.log 2>&1
fi

# Serve the built frontend using Python's HTTP server (much faster than dev server)
echo "Starting frontend server on port 3000..."
cd build
python3 -m http.server 3000 --bind 0.0.0.0 >../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "Frontend PID: $FRONTEND_PID (serving built files)"
echo ""

echo "=========================================="
echo "Services Starting in Background"
echo "=========================================="
echo ""
echo "Backend API: http://localhost:8000 (PID: $BACKEND_PID)"
echo "API Docs: http://localhost:8000/docs"
echo "Frontend UI: http://localhost:3000 (PID: $FRONTEND_PID)"
echo "Stats API: http://localhost:8000/api/stats"
echo ""
echo "Note: Services are starting in the background."
echo "      Frontend is serving built files (fast startup)."
echo ""
echo "To stop services: ./stop.sh"
echo "To view logs: tail -f backend.log frontend.log"
echo ""

