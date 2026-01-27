#!/bin/bash

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Building Infrastructure Integration System"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BUILD_MODE=${1:-"without-docker"}

# Verify we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "Error: backend or frontend directory not found. Please run from infrastructure-integration-testing directory."
    exit 1
fi

if [ "$BUILD_MODE" = "docker" ]; then
    echo -e "${GREEN}Building with Docker...${NC}"
    
    # Check if docker-compose.yml exists
    if [ ! -f "docker-compose.yml" ]; then
        echo "Error: docker-compose.yml not found"
        exit 1
    fi
    
    echo "Building Docker images..."
    docker-compose build
    
    echo "Starting services..."
    docker-compose up -d
    
    echo "Waiting for services to be ready..."
    sleep 10
    
    echo -e "${GREEN}Services started!${NC}"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
    
else
    echo -e "${GREEN}Building without Docker...${NC}"
    
    # Backend setup
    echo "Setting up backend..."
    BACKEND_DIR="$SCRIPT_DIR/backend"
    cd "$BACKEND_DIR"
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        echo "Error: backend/requirements.txt not found"
        exit 1
    fi
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    
    # Check if backend is already running
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "Warning: Port 8000 is already in use. Stopping existing process..."
        pkill -f "uvicorn app.main:app" || true
        sleep 2
    fi
    
    echo "Starting backend server..."
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$SCRIPT_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$SCRIPT_DIR/backend.pid"
    
    cd "$SCRIPT_DIR"
    
    # Frontend setup
    echo "Setting up frontend..."
    FRONTEND_DIR="$SCRIPT_DIR/frontend"
    cd "$FRONTEND_DIR"
    
    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        echo "Error: frontend/package.json not found"
        exit 1
    fi
    
    if [ ! -d "node_modules" ]; then
        npm install --silent
    fi
    
    # Check if frontend is already running
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "Warning: Port 3000 is already in use. Stopping existing process..."
        pkill -f "react-scripts start" || true
        sleep 2
    fi
    
    echo "Starting frontend server..."
    nohup npm start > "$SCRIPT_DIR/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$SCRIPT_DIR/frontend.pid"
    
    cd "$SCRIPT_DIR"
    
    echo "Waiting for services to start..."
    sleep 15
    
    echo -e "${GREEN}Services started!${NC}"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
    
    # Run tests
    echo ""
    echo "Running integration tests..."
    cd "$BACKEND_DIR"
    source venv/bin/activate
    pytest tests/integration/ -v
    cd "$SCRIPT_DIR"
fi

echo ""
echo -e "${GREEN}Build complete!${NC}"
echo ""
echo "To run integration tests:"
echo "  curl -X POST http://localhost:8000/api/v1/integration/tests/run -H 'Content-Type: application/json' -d '{\"test_type\": \"end_to_end\", \"cloud_provider\": \"aws\", \"resource_count\": 10, \"duration_minutes\": 5, \"chaos_enabled\": false}'"
echo ""
echo "View test results:"
echo "  curl http://localhost:8000/api/v1/integration/tests"
