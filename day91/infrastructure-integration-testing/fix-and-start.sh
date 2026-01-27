#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Fix and Start Services${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check backend
echo -e "${GREEN}Checking backend...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running on http://localhost:8000${NC}"
else
    echo -e "${YELLOW}Backend is not running. Starting backend...${NC}"
    cd backend
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -q -r requirements.txt
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
    echo $! > ../backend.pid
    cd ..
    sleep 5
    echo -e "${GREEN}✓ Backend started${NC}"
fi

# Check and fix frontend
echo ""
echo -e "${GREEN}Checking frontend...${NC}"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
cd "$FRONTEND_DIR"

# Wait for any running npm install to complete
if pgrep -f "npm install" > /dev/null; then
    echo -e "${YELLOW}Waiting for npm install to complete (this may take a few minutes)...${NC}"
    while pgrep -f "npm install" > /dev/null; do
        echo -n "."
        sleep 5
    done
    echo ""
    echo -e "${GREEN}npm install completed${NC}"
fi

# Ensure dependencies are installed
if [ ! -d "node_modules" ] || [ ! -f "node_modules/.bin/react-scripts" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

# Fix permissions
echo -e "${GREEN}Fixing permissions...${NC}"
if [ -d "node_modules/.bin" ]; then
    find node_modules/.bin -type f -exec chmod +x {} \; 2>/dev/null || true
fi

# Check if frontend is already running
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}Port 3000 is already in use.${NC}"
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend is already running on http://localhost:3000${NC}"
        exit 0
    else
        echo -e "${YELLOW}Stopping existing process...${NC}"
        pkill -f "react-scripts start" || true
        pkill -f "npm start" || true
        sleep 2
    fi
fi

# Start frontend using npx to avoid permission issues
echo -e "${GREEN}Starting frontend server...${NC}"
cd "$FRONTEND_DIR"
BROWSER=none nohup npx react-scripts start > "$SCRIPT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$SCRIPT_DIR/frontend.pid"

echo -e "${GREEN}Frontend server starting (PID: $FRONTEND_PID)${NC}"
echo -e "${YELLOW}Waiting for frontend to be ready (this may take 30-60 seconds)...${NC}"

# Wait for frontend to be ready
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✓ Frontend is running on http://localhost:3000${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

echo ""
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Services Status${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Backend:  http://localhost:8000"
echo -e "Frontend: http://localhost:3000"
echo -e "API Docs: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}If frontend is not accessible, check logs:${NC}"
echo -e "  tail -f $SCRIPT_DIR/frontend.log"
echo ""
