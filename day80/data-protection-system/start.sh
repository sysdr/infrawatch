#!/bin/bash

set -e

echo "========================================="
echo "Day 80: Data Protection System - Start"
echo "========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

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

echo -e "${YELLOW}Starting Data Protection System...${NC}"

# Check for duplicate services
if check_port 8000; then
    echo -e "${YELLOW}Port 8000 is already in use. Checking for existing backend...${NC}"
    if check_process "uvicorn.*app.main:app"; then
        echo -e "${GREEN}Backend service already running.${NC}"
        BACKEND_RUNNING=true
    else
        echo -e "${RED}Port 8000 is in use by another process. Please free the port.${NC}"
        exit 1
    fi
fi

if check_port 3000; then
    echo -e "${YELLOW}Port 3000 is already in use. Checking for existing frontend...${NC}"
    if check_process "react-scripts start"; then
        echo -e "${GREEN}Frontend service already running.${NC}"
        FRONTEND_RUNNING=true
    else
        echo -e "${RED}Port 3000 is in use by another process. Please free the port.${NC}"
        exit 1
    fi
fi

# Setup and start backend
if [ -z "$BACKEND_RUNNING" ]; then
    echo -e "${YELLOW}Starting backend...${NC}"
    cd "$PROJECT_ROOT/backend"
    
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    if [ ! -f "venv/.installed" ]; then
        echo -e "${YELLOW}Installing dependencies...${NC}"
        pip install -q -r requirements.txt
        touch venv/.installed
    fi
    
    # Ensure database exists
    export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5433/dataprotection}"
    
    # Run backend
    echo -e "${YELLOW}Starting backend server...${NC}"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$PROJECT_ROOT/.backend.pid"
    echo -e "${GREEN}Backend started with PID: $BACKEND_PID${NC}"
    sleep 3
fi

# Setup and start frontend
if [ -z "$FRONTEND_RUNNING" ]; then
    echo -e "${YELLOW}Starting frontend...${NC}"
    cd "$PROJECT_ROOT/frontend"
    
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing dependencies...${NC}"
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

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Services started successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}To stop services, run: ./stop.sh${NC}"
echo ""
