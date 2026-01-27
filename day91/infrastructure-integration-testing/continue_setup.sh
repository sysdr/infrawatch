#!/bin/bash

# Continue setup script - fixes frontend and ensures everything is running

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$(dirname "$0")"

echo -e "${GREEN}Continuing setup...${NC}"
echo ""

# Check if npm install is still running
if pgrep -f "npm install" > /dev/null; then
    echo -e "${YELLOW}Waiting for npm install to complete...${NC}"
    while pgrep -f "npm install" > /dev/null; do
        sleep 3
        echo -n "."
    done
    echo ""
    echo -e "${GREEN}npm install completed${NC}"
fi

# Fix permissions for node_modules/.bin
echo "Fixing permissions for node_modules binaries..."
cd frontend
if [ -d "node_modules/.bin" ]; then
    chmod +x node_modules/.bin/* 2>/dev/null || true
    echo -e "${GREEN}Permissions fixed${NC}"
else
    echo -e "${YELLOW}node_modules/.bin not found, ensuring npm install completed...${NC}"
    npm install --silent
    chmod +x node_modules/.bin/* 2>/dev/null || true
fi

# Stop any existing frontend process
if [ -f "../frontend.pid" ]; then
    kill $(cat ../frontend.pid) 2>/dev/null || true
    rm ../frontend.pid
fi

# Start frontend
echo "Starting frontend server..."
nohup npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
echo -e "${GREEN}Frontend started (PID: $FRONTEND_PID)${NC}"

# Wait a bit for frontend to start
echo "Waiting for frontend to initialize..."
sleep 10

# Check backend status
echo ""
echo "Checking services..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ Backend is running on http://localhost:8000${NC}"
else
    echo -e "${YELLOW}⚠ Backend is not responding${NC}"
fi

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is running on http://localhost:3000${NC}"
else
    echo -e "${YELLOW}⚠ Frontend is starting (may take 30-60 seconds)${NC}"
fi

echo ""
echo -e "${GREEN}Setup continuation complete!${NC}"
echo ""
echo "Services:"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "To check logs:"
echo "  tail -f backend.log"
echo "  tail -f frontend.log"
