#!/bin/bash

# Finalize frontend setup - run this after npm install completes

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

cd "$(dirname "$0")/frontend"

echo -e "${GREEN}Finalizing frontend setup...${NC}"
echo ""

# Check if npm install is still running
if pgrep -f "npm install" > /dev/null; then
    echo -e "${YELLOW}npm install is still running. Please wait for it to complete.${NC}"
    echo "You can check status with: ps aux | grep 'npm install'"
    exit 1
fi

# Check if react-scripts is installed
if [ ! -f "node_modules/.bin/react-scripts" ]; then
    echo -e "${RED}react-scripts not found. Running npm install...${NC}"
    npm install
fi

# Fix permissions
echo "Fixing permissions for node_modules binaries..."
if [ -d "node_modules/.bin" ]; then
    chmod +x node_modules/.bin/* 2>/dev/null || true
    echo -e "${GREEN}✓ Permissions fixed${NC}"
else
    echo -e "${RED}✗ node_modules/.bin directory not found${NC}"
    exit 1
fi

# Stop any existing frontend process
cd ..
if [ -f "frontend.pid" ]; then
    OLD_PID=$(cat frontend.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "Stopping existing frontend process (PID: $OLD_PID)..."
        kill $OLD_PID 2>/dev/null || true
        sleep 2
    fi
    rm frontend.pid
fi

# Start frontend
echo "Starting frontend server..."
cd frontend
nohup npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"

# Wait for frontend to start
echo "Waiting for frontend to initialize (this may take 30-60 seconds)..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend is now accessible at http://localhost:3000${NC}"
        break
    fi
    echo -n "."
    sleep 2
done
echo ""

# Final status check
echo ""
echo -e "${GREEN}=== Service Status ===${NC}"
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ Backend: http://localhost:8000${NC}"
else
    echo -e "${RED}✗ Backend: Not responding${NC}"
fi

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend: http://localhost:3000${NC}"
else
    echo -e "${YELLOW}⚠ Frontend: Starting (check frontend.log for details)${NC}"
fi

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "Access the application:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "View logs:"
echo "  tail -f frontend.log"
echo "  tail -f backend.log"
