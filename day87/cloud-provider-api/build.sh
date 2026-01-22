#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================="
echo "Building Cloud Provider API System"
echo "=================================="

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to check for duplicate services
check_duplicate_services() {
    echo "Checking for duplicate services..."
    
    if check_port 8000; then
        echo "WARNING: Port 8000 is already in use. Backend may already be running."
        echo "Checking if it's our backend..."
        if pgrep -f "uvicorn.*app.main:app" > /dev/null; then
            echo "Found existing backend process. Stopping it..."
            pkill -f "uvicorn.*app.main:app"
            sleep 2
        fi
    fi
    
    if check_port 3000; then
        echo "WARNING: Port 3000 is already in use. Frontend may already be running."
        echo "Checking if it's our frontend..."
        if pgrep -f "react-scripts start" > /dev/null; then
            echo "Found existing frontend process. Stopping it..."
            pkill -f "react-scripts start"
            sleep 2
        fi
    fi
    
    if check_port 5432; then
        echo "INFO: PostgreSQL is running on port 5432"
    else
        echo "WARNING: PostgreSQL is not running on port 5432"
    fi
    
    if check_port 6379; then
        echo "INFO: Redis is running on port 6379"
    else
        echo "WARNING: Redis is not running on port 6379"
    fi
}

# Check if running with Docker flag
USE_DOCKER=false
if [ "$1" == "--docker" ]; then
    USE_DOCKER=true
fi

if [ "$USE_DOCKER" == true ]; then
    echo "Building with Docker..."
    
    DOCKER_DIR="$SCRIPT_DIR/docker"
    if [ ! -d "$DOCKER_DIR" ]; then
        echo "ERROR: Docker directory not found at $DOCKER_DIR"
        exit 1
    fi
    
    DOCKER_COMPOSE_FILE="$DOCKER_DIR/docker-compose.yml"
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        echo "ERROR: docker-compose.yml not found at $DOCKER_COMPOSE_FILE"
        exit 1
    fi
    
    cd "$DOCKER_DIR"
    docker-compose up -d
    
    echo "Waiting for services to be healthy..."
    sleep 10
    
    echo "✓ Services started with Docker"
    echo ""
    echo "Access the application:"
    echo "- Frontend: http://localhost:3000"
    echo "- Backend API: http://localhost:8000"
    echo "- API Docs: http://localhost:8000/docs"
    echo ""
    echo "To stop: cd $DOCKER_DIR && docker-compose down"
else
    echo "Building without Docker..."
    
    # Check for duplicate services
    check_duplicate_services
    
    # Backend setup
    echo "Setting up backend..."
    BACKEND_DIR="$SCRIPT_DIR/backend"
    if [ ! -d "$BACKEND_DIR" ]; then
        echo "ERROR: Backend directory not found at $BACKEND_DIR"
        exit 1
    fi
    
    cd "$BACKEND_DIR"
    
    # Check if venv exists, create if not
    if [ ! -d "venv" ]; then
        echo "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate venv
    source venv/bin/activate
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        echo "ERROR: requirements.txt not found in $BACKEND_DIR"
        exit 1
    fi
    
    echo "Installing Python dependencies..."
    pip install -q -r requirements.txt
    
    # Initialize database
    echo "Initializing database..."
    python3 -c "
import asyncio
import sys
sys.path.insert(0, '.')
from app.models.database import init_db
asyncio.run(init_db())
" || echo "WARNING: Database initialization failed (may need PostgreSQL running)"
    
    # Start backend
    echo "Starting backend server..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!
    sleep 3
    
    # Verify backend started
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "ERROR: Backend failed to start. Check /tmp/backend.log"
        exit 1
    fi
    
    # Frontend setup
    echo "Setting up frontend..."
    FRONTEND_DIR="$SCRIPT_DIR/frontend"
    if [ ! -d "$FRONTEND_DIR" ]; then
        echo "ERROR: Frontend directory not found at $FRONTEND_DIR"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    
    cd "$FRONTEND_DIR"
    
    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        echo "ERROR: package.json not found in $FRONTEND_DIR"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    
    # Check if node_modules exists, install if not
    if [ ! -d "node_modules" ]; then
        echo "Installing Node.js dependencies..."
        npm install
    fi
    
    echo "Starting frontend server..."
    npm start > /tmp/frontend.log 2>&1 &
    FRONTEND_PID=$!
    sleep 5
    
    # Verify frontend started
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "ERROR: Frontend failed to start. Check /tmp/frontend.log"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    
    echo "✓ Services started"
    echo ""
    echo "Access the application:"
    echo "- Frontend: http://localhost:3000"
    echo "- Backend API: http://localhost:8000"
    echo "- API Docs: http://localhost:8000/docs"
    echo ""
    echo "Backend PID: $BACKEND_PID"
    echo "Frontend PID: $FRONTEND_PID"
    echo "Backend logs: /tmp/backend.log"
    echo "Frontend logs: /tmp/frontend.log"
    
    # Save PIDs for stop script
    echo $BACKEND_PID > "$SCRIPT_DIR/.backend.pid"
    echo $FRONTEND_PID > "$SCRIPT_DIR/.frontend.pid"
fi
