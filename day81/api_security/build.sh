#!/bin/bash

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}Day 81: API Security - Build Script${NC}"
echo -e "${BLUE}=====================================${NC}"

# Check if running with Docker
USE_DOCKER=${1:-"no"}

if [ "$USE_DOCKER" = "docker" ]; then
    echo -e "${GREEN}Building and running with Docker...${NC}"
    
    cd docker
    docker-compose down -v
    docker-compose up --build -d
    
    echo -e "${GREEN}Waiting for services to be healthy...${NC}"
    sleep 10
    
    echo -e "${GREEN}✓ Docker services started${NC}"
    echo -e "${BLUE}Backend API: http://localhost:8000${NC}"
    echo -e "${BLUE}Frontend Dashboard: http://localhost:3000${NC}"
    echo -e "${BLUE}API Docs: http://localhost:8000/docs${NC}"
    
    echo ""
    echo -e "${GREEN}To view logs: docker-compose logs -f${NC}"
    echo -e "${GREEN}To stop: docker-compose down${NC}"
    
else
    echo -e "${GREEN}Building and running without Docker...${NC}"
    
    # Backend setup
    echo -e "${BLUE}Setting up backend...${NC}"
    cd backend
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
    
    # Start backend in background
    echo -e "${BLUE}Starting backend server...${NC}"
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    
    cd ..
    
    # Frontend setup
    echo -e "${BLUE}Setting up frontend...${NC}"
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        npm install --silent
    fi
    
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
    
    # Start frontend in background
    echo -e "${BLUE}Starting frontend server...${NC}"
    npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    
    cd ..
    
    echo -e "${GREEN}Waiting for servers to start...${NC}"
    sleep 5
    
    echo -e "${GREEN}✓ Servers started${NC}"
    echo -e "${BLUE}Backend API: http://localhost:8000${NC}"
    echo -e "${BLUE}Frontend Dashboard: http://localhost:3000${NC}"
    echo -e "${BLUE}API Docs: http://localhost:8000/docs${NC}"
    
    echo ""
    echo -e "${GREEN}Running tests...${NC}"
    cd backend
    source venv/bin/activate
    export PYTHONPATH=$(pwd)
    pytest ../tests/unit -v --tb=short
    cd ..
    
    echo ""
    echo -e "${GREEN}✓ Build and tests completed successfully!${NC}"
    echo -e "${BLUE}Backend logs: tail -f backend.log${NC}"
    echo -e "${BLUE}Frontend logs: tail -f frontend.log${NC}"
    echo -e "${BLUE}To stop: ./stop.sh${NC}"
fi
