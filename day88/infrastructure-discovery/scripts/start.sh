#!/bin/bash

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Starting Infrastructure Discovery System..."
echo "Project root: $PROJECT_ROOT"

# Check for duplicate services
echo "Checking for existing services..."

# Check if backend is already running on port 8000
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "WARNING: Port 8000 is already in use. Stopping existing backend..."
    (lsof -Pi :8000 -sTCP:LISTEN -t | xargs -r kill -9) 2>/dev/null || true
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    sleep 3
fi

# Check if frontend is already running on port 3001
if lsof -Pi :3001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "WARNING: Port 3001 is already in use. Stopping existing frontend..."
    (lsof -Pi :3001 -sTCP:LISTEN -t | xargs -r kill -9) 2>/dev/null || true
    pkill -f "react-scripts start" 2>/dev/null || true
    sleep 3
fi

# Check if Docker services are already running
if docker ps | grep -q "day88.*postgres\|infrastructure-discovery.*postgres"; then
    echo "Docker services may already be running. Checking..."
fi

# Start PostgreSQL and Redis with Docker
echo "Starting PostgreSQL and Redis..."
DOCKER_DIR="$PROJECT_ROOT/docker"
if [ ! -d "$DOCKER_DIR" ]; then
    echo "ERROR: Docker directory not found at $DOCKER_DIR"
    exit 1
fi

cd "$DOCKER_DIR"
if [ ! -f "docker-compose.yml" ]; then
    echo "ERROR: docker-compose.yml not found"
    exit 1
fi

docker-compose up -d postgres redis
cd "$PROJECT_ROOT"

# Wait for services
echo "Waiting for services to be ready..."
sleep 5

# Check if backend venv exists
BACKEND_DIR="$PROJECT_ROOT/backend"
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "ERROR: Backend virtual environment not found. Please run ./scripts/build.sh first"
    exit 1
fi

# Start backend
echo "Starting backend..."
cd "$BACKEND_DIR"
if [ ! -f "venv/bin/activate" ]; then
    echo "ERROR: Virtual environment activation script not found"
    exit 1
fi

source venv/bin/activate
if ! command -v uvicorn &> /dev/null; then
    echo "ERROR: uvicorn not found. Please run ./scripts/build.sh first"
    exit 1
fi

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd "$PROJECT_ROOT"

# Wait for backend
echo "Waiting for backend to start..."
sleep 5

# Check if frontend node_modules exists
FRONTEND_DIR="$PROJECT_ROOT/frontend"
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "ERROR: Frontend node_modules not found. Please run ./scripts/build.sh first"
    exit 1
fi

# Start frontend
echo "Starting frontend..."
cd "$FRONTEND_DIR"
if [ ! -f "package.json" ]; then
    echo "ERROR: package.json not found"
    exit 1
fi

HOST=0.0.0.0 DANGEROUSLY_DISABLE_HOST_CHECK=true PORT=3001 npm start &
FRONTEND_PID=$!
cd "$PROJECT_ROOT"

echo "==============================================="
echo "Infrastructure Discovery System is running!"
echo "==============================================="
echo "Frontend: http://localhost:3001"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Save PIDs
echo $BACKEND_PID > /tmp/discovery_backend.pid
echo $FRONTEND_PID > /tmp/discovery_frontend.pid

# Wait for user interrupt
wait
