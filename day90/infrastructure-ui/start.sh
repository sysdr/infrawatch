#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo "======================================"
echo "Infrastructure UI - Startup Script"
echo "======================================"
echo "Working directory: $SCRIPT_DIR"

# Check for duplicate services
echo ""
echo "Checking for duplicate services..."
EXISTING_BACKEND=$(ps aux | grep "[u]vicorn.*8000" | wc -l)
EXISTING_FRONTEND=$(ps aux | grep "[n]ode.*vite\|[n]pm.*dev" | grep -v grep | wc -l)

if [ "$EXISTING_BACKEND" -gt 0 ]; then
    echo "WARNING: Backend service already running on port 8000"
    ps aux | grep "[u]vicorn.*8000"
    read -p "Kill existing backend? (y/n): " kill_backend
    if [ "$kill_backend" = "y" ]; then
        pkill -f "uvicorn.*8000"
        sleep 2
    else
        echo "Exiting. Please stop existing services first."
        exit 1
    fi
fi

if [ "$EXISTING_FRONTEND" -gt 0 ]; then
    echo "WARNING: Frontend service may already be running"
    ps aux | grep "[n]ode.*vite\|[n]pm.*dev" | grep -v grep
    read -p "Kill existing frontend? (y/n): " kill_frontend
    if [ "$kill_frontend" = "y" ]; then
        pkill -f "vite\|npm.*dev"
        sleep 2
    fi
fi

# Check if database exists, create if not
echo ""
echo "Checking database..."
cd "$SCRIPT_DIR/backend" || exit 1
source venv/bin/activate 2>/dev/null || {
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -q fastapi uvicorn sqlalchemy asyncpg pydantic pydantic-settings redis websockets pytest pytest-asyncio httpx
}

# Try to create database if it doesn't exist
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5433/infradb"
export REDIS_URL="redis://localhost:6379"

python3 << 'PYTHON_SCRIPT'
import asyncio
import asyncpg
import sys

async def check_db():
    try:
        # Try to connect to postgres database first
        conn = await asyncpg.connect(
            host='localhost',
            port=5433,
            user='postgres',
            password='postgres',
            database='postgres'
        )
        # Check if infradb exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname='infradb'"
        )
        if not exists:
            await conn.execute('CREATE DATABASE infradb')
            print("✓ Database 'infradb' created")
        else:
            print("✓ Database 'infradb' already exists")
        await conn.close()
    except Exception as e:
        print(f"Note: Could not create database automatically: {e}")
        print("Database will be created on first connection if permissions allow")

asyncio.run(check_db())
PYTHON_SCRIPT

# Start backend
echo ""
echo "Starting backend server..."
cd "$SCRIPT_DIR/backend" || exit 1
source venv/bin/activate
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5433/infradb"
export REDIS_URL="redis://localhost:6379"

uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
echo "$BACKEND_PID" > "$SCRIPT_DIR/.backend.pid"

# Wait for backend to be ready
echo "Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Backend is ready"
        break
    fi
    sleep 1
done

# Start frontend
echo ""
echo "Starting frontend server..."
cd "$SCRIPT_DIR/frontend" || exit 1

if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"
echo "$FRONTEND_PID" > "$SCRIPT_DIR/.frontend.pid"

# Wait a bit for frontend
sleep 3

echo ""
echo "======================================"
echo "✓ Services started successfully!"
echo "======================================"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Access the application:"
echo "  Frontend: http://localhost:5173"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Health: http://localhost:8000/health"
echo ""
echo "Logs:"
echo "  Backend: tail -f /tmp/backend.log"
echo "  Frontend: tail -f /tmp/frontend.log"
echo ""
echo "To stop services: ./stop.sh"
echo ""
