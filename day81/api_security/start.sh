#!/bin/bash

# Start script for API Security System
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}Day 81: API Security - Start Script${NC}"
echo -e "${BLUE}=====================================${NC}"

# Check if services are already running
BACKEND_RUNNING=$(ps aux | grep -E "uvicorn app.main" | grep -v grep | wc -l)
FRONTEND_RUNNING=$(ps aux | grep -E "vite" | grep -v grep | wc -l)

if [ "$BACKEND_RUNNING" -gt 0 ] || [ "$FRONTEND_RUNNING" -gt 0 ]; then
    echo -e "${YELLOW}Services appear to be already running.${NC}"
    echo -e "${YELLOW}Backend processes: $BACKEND_RUNNING${NC}"
    echo -e "${YELLOW}Frontend processes: $FRONTEND_RUNNING${NC}"
    echo -e "${YELLOW}Stopping existing services...${NC}"
    ./stop.sh
    sleep 2
    # Force kill any remaining processes
    pkill -f "uvicorn app.main" 2>/dev/null || true
    pkill -f "node.*vite" 2>/dev/null || true
    sleep 1
fi

# Start Docker containers (PostgreSQL and Redis)
echo -e "${BLUE}Starting Docker containers (PostgreSQL and Redis)...${NC}"
cd docker
if docker-compose ps | grep -q "postgres.*Up\|redis.*Up"; then
    echo -e "${GREEN}✓ Docker containers already running${NC}"
else
    docker-compose up -d postgres redis
    echo -e "${GREEN}Waiting for containers to be healthy...${NC}"
    sleep 5
    echo -e "${GREEN}✓ Docker containers started${NC}"
fi
cd ..

# Start backend
echo -e "${BLUE}Starting backend server...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies if needed
if [ ! -d "venv/lib/python3.11/site-packages/fastapi" ]; then
    echo -e "${BLUE}Installing backend dependencies...${NC}"
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
fi

# Start backend in background
export PYTHONPATH=$(pwd)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"

cd ..

# Start frontend
echo -e "${BLUE}Starting frontend server...${NC}"
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}Installing frontend dependencies...${NC}"
    npm install --silent
fi

# Start frontend in background
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"

cd ..

# Wait for services to be ready
echo -e "${BLUE}Waiting for services to be ready...${NC}"
sleep 5

# Verify services
MAX_RETRIES=10
RETRY=0
BACKEND_READY=false
FRONTEND_READY=false

while [ $RETRY -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        BACKEND_READY=true
    fi
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        FRONTEND_READY=true
    fi
    
    if [ "$BACKEND_READY" = true ] && [ "$FRONTEND_READY" = true ]; then
        break
    fi
    
    RETRY=$((RETRY + 1))
    sleep 2
done

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}✓ Services started successfully!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo -e "${BLUE}Backend API:${NC}      http://localhost:8000"
echo -e "${BLUE}Frontend Dashboard:${NC} http://localhost:3000"
echo -e "${BLUE}API Docs:${NC}          http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo -e "  View backend logs:  tail -f backend.log"
echo -e "  View frontend logs: tail -f frontend.log"
echo -e "  Stop services:     ./stop.sh"
echo -e "  Run demo:          ./demo.sh"
echo ""

if [ "$BACKEND_READY" = false ] || [ "$FRONTEND_READY" = false ]; then
    echo -e "${YELLOW}Warning: Some services may not be fully ready yet.${NC}"
    echo -e "${YELLOW}Backend ready: $BACKEND_READY${NC}"
    echo -e "${YELLOW}Frontend ready: $FRONTEND_READY${NC}"
    echo -e "${YELLOW}Check logs for details.${NC}"
fi
