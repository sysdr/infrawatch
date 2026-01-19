#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Starting Security Testing Platform ==="

# Start Docker services (PostgreSQL and Redis)
echo "Starting Docker services..."
docker-compose up -d postgres redis
sleep 5

# Check if PostgreSQL is ready
echo "Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
        echo "✓ PostgreSQL is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "Error: PostgreSQL did not become ready in time"
        exit 1
    fi
    sleep 1
done

# Check if backend venv exists
if [ ! -d "backend/venv" ]; then
    echo "Error: Backend virtual environment not found. Please run ./build.sh first."
    exit 1
fi

# Start backend server
echo "Starting backend server..."
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
export PYTHONPATH="$SCRIPT_DIR/backend:$PYTHONPATH"

# Check if backend is already running
if lsof -i :8000 >/dev/null 2>&1; then
    echo "Backend is already running on port 8000"
else
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"
    sleep 3
    
    # Verify backend is running
    if curl -s http://localhost:8000/ >/dev/null 2>&1; then
        echo "✓ Backend is running on http://localhost:8000"
    else
        echo "Warning: Backend may not have started correctly. Check /tmp/backend.log"
    fi
fi

# Check if frontend node_modules exists
if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd "$SCRIPT_DIR/frontend"
    npm install
fi

# Start frontend server
echo "Starting frontend server..."
cd "$SCRIPT_DIR/frontend"

# Check if frontend is already running
if lsof -i :3000 >/dev/null 2>&1; then
    echo "Frontend is already running on port 3000"
else
    # Check if build exists, if not create it
    if [ ! -d "build" ]; then
        echo "Building frontend for production..."
        npm run build
    fi
    
    # Start Python HTTP server to serve the build
    cd "$SCRIPT_DIR/frontend/build"
    python3 -m http.server 3000 > /tmp/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "Frontend started with PID: $FRONTEND_PID"
    sleep 3
    
    # Verify frontend is running
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo "✓ Frontend is running on http://localhost:3000"
    else
        echo "Warning: Frontend may not have started correctly. Check /tmp/frontend.log"
    fi
fi

echo ""
echo "=== Services Started ==="
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "To stop services, run: ./stop.sh"
echo ""
