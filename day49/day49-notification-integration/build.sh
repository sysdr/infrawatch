#!/bin/bash

set -e

echo "============================================"
echo "Building Notification Integration System"
echo "============================================"
echo ""

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if Docker is requested
if [ "$1" = "--docker" ]; then
    echo -e "${BLUE}Building with Docker...${NC}"
    docker-compose down -v 2>/dev/null || true
    docker-compose up -d --build
    
    echo -e "${BLUE}Waiting for services to be ready...${NC}"
    sleep 20
    
    echo -e "${GREEN}✓ Services started with Docker${NC}"
    echo ""
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo ""
    echo "Run './stop.sh' to stop all services"
    exit 0
fi

# Non-Docker build
echo -e "${BLUE}Building without Docker (local)...${NC}"

# Backend setup
echo -e "${BLUE}Setting up backend...${NC}"
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# Start services in background (requires local postgres and redis)
echo -e "${BLUE}Starting backend server...${NC}"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid

cd ..

# Frontend setup
echo -e "${BLUE}Setting up frontend...${NC}"
cd frontend

npm install

echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

echo -e "${BLUE}Starting frontend server...${NC}"
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid

cd ..

echo ""
echo -e "${GREEN}✓ Build complete!${NC}"
echo ""
echo "Services starting..."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Logs:"
echo "  Backend: tail -f backend.log"
echo "  Frontend: tail -f frontend.log"
echo ""
echo "Run './stop.sh' to stop all services"
