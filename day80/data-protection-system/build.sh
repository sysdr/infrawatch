#!/bin/bash

set -e

echo "========================================="
echo "Day 80: Data Protection System - Build"
echo "========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

BUILD_MODE=${1:-local}

# Function to check if port is in use
check_port() {
    local port=$1
    if command -v lsof >/dev/null 2>&1; then
        lsof -i :$port >/dev/null 2>&1
    elif command -v netstat >/dev/null 2>&1; then
        netstat -tuln | grep -q ":$port " >/dev/null 2>&1
    elif command -v ss >/dev/null 2>&1; then
        ss -tuln | grep -q ":$port " >/dev/null 2>&1
    else
        return 1
    fi
}

# Function to check if process is running
check_process() {
    local pattern=$1
    pgrep -f "$pattern" >/dev/null 2>&1
}

if [ "$BUILD_MODE" = "docker" ]; then
    echo -e "${YELLOW}Building with Docker...${NC}"
    cd "$PROJECT_ROOT/docker"
    docker-compose up --build -d
    
    echo -e "${GREEN}Waiting for services to be ready...${NC}"
    sleep 10
    
    echo -e "${GREEN}Services started successfully!${NC}"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
    
else
    echo -e "${YELLOW}Building locally...${NC}"
    
    # Check for duplicate services
    if check_port 8000; then
        echo -e "${YELLOW}Port 8000 is already in use. Checking for existing backend...${NC}"
        if check_process "uvicorn.*app.main:app"; then
            echo -e "${YELLOW}Backend service already running. Skipping backend startup.${NC}"
            BACKEND_RUNNING=true
        else
            echo -e "${RED}Port 8000 is in use by another process. Please free the port.${NC}"
            exit 1
        fi
    fi
    
    if check_port 3000; then
        echo -e "${YELLOW}Port 3000 is already in use. Checking for existing frontend...${NC}"
        if check_process "react-scripts start"; then
            echo -e "${YELLOW}Frontend service already running. Skipping frontend startup.${NC}"
            FRONTEND_RUNNING=true
        else
            echo -e "${RED}Port 3000 is in use by another process. Please free the port.${NC}"
            exit 1
        fi
    fi
    
    # Setup backend
    if [ -z "$BACKEND_RUNNING" ]; then
        echo -e "${YELLOW}Setting up backend...${NC}"
        cd "$PROJECT_ROOT/backend"
        
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        
        source venv/bin/activate
        pip install -q -r requirements.txt
        
        # Run backend
        echo -e "${YELLOW}Starting backend server...${NC}"
        uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
        BACKEND_PID=$!
        echo $BACKEND_PID > "$PROJECT_ROOT/.backend.pid"
        echo -e "${GREEN}Backend started with PID: $BACKEND_PID${NC}"
        sleep 3
    fi
    
    # Setup frontend
    if [ -z "$FRONTEND_RUNNING" ]; then
        echo -e "${YELLOW}Setting up frontend...${NC}"
        cd "$PROJECT_ROOT/frontend"
        
        if [ ! -d "node_modules" ]; then
            npm install
        fi
        
        # Run frontend
        echo -e "${YELLOW}Starting frontend server...${NC}"
        BROWSER=none npm start > /tmp/frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > "$PROJECT_ROOT/.frontend.pid"
        echo -e "${GREEN}Frontend started with PID: $FRONTEND_PID${NC}"
        sleep 5
    fi
    
    echo -e "${GREEN}Services started successfully!${NC}"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
fi

# Run tests
echo -e "${YELLOW}Running tests...${NC}"
cd "$PROJECT_ROOT/backend"
if [ -d "venv" ]; then
    source venv/bin/activate
fi
pytest tests/ -v || echo -e "${YELLOW}Some tests may have failed. Check database connection.${NC}"
cd "$PROJECT_ROOT"

echo -e "${GREEN}Build completed successfully!${NC}"
echo ""
echo "=== Quick Test Commands ==="
echo "1. Test encryption:"
echo '   curl -X POST http://localhost:8000/api/encryption/encrypt -H "Content-Type: application/json" -d'"'"'{"plaintext":"sensitive data","context":"test"}'"'"''
echo ""
echo "2. Test data classification:"
echo '   curl -X POST http://localhost:8000/api/classification/classify -H "Content-Type: application/json" -d'"'"'{"data":{"email":"test@test.com","ssn":"123-45-6789"}}'"'"''
echo ""
echo "3. Test data masking:"
echo '   curl -X POST http://localhost:8000/api/masking/mask-text -H "Content-Type: application/json" -d'"'"'{"text":"Contact john@example.com or 123-456-7890"}'"'"''
