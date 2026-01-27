#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

cd "$FRONTEND_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Starting Frontend Server${NC}"
echo ""

# Wait for npm install to complete
if pgrep -f "npm install" > /dev/null; then
    echo -e "${YELLOW}Waiting for npm install to complete...${NC}"
    while pgrep -f "npm install" > /dev/null; do
        echo -n "."
        sleep 3
    done
    echo ""
    echo -e "${GREEN}npm install completed!${NC}"
fi

# Verify dependencies are installed
if [ ! -f "node_modules/.bin/react-scripts" ]; then
    echo -e "${YELLOW}Dependencies not found. Installing...${NC}"
    npm install
fi

# Check for critical dependencies
if [ ! -d "node_modules/@mui/material" ] || [ ! -d "node_modules/recharts" ]; then
    echo -e "${YELLOW}Missing dependencies detected. Reinstalling...${NC}"
    npm install
fi

# Fix permissions
echo -e "${GREEN}Fixing permissions...${NC}"
if [ -d "node_modules/.bin" ]; then
    chmod +x node_modules/.bin/* 2>/dev/null || true
fi

# Stop any existing frontend
echo -e "${GREEN}Stopping any existing frontend processes...${NC}"
pkill -f "react-scripts start" 2>/dev/null || true
pkill -f "npm.*start" 2>/dev/null || true
sleep 2

# Check if port is in use
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}Port 3000 is in use. Clearing...${NC}"
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Start frontend
echo -e "${GREEN}Starting frontend server on port 3000...${NC}"
cd "$FRONTEND_DIR"
BROWSER=none nohup npm start > "$SCRIPT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$SCRIPT_DIR/frontend.pid"

echo -e "${GREEN}Frontend started (PID: $FRONTEND_PID)${NC}"
echo -e "${YELLOW}Waiting for compilation (this may take 30-60 seconds)...${NC}"

# Wait for frontend to be ready
for i in {1..40}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✓ Frontend is now accessible at http://localhost:3000${NC}"
        exit 0
    fi
    # Check if process is still running
    if ! ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo ""
        echo -e "${RED}Frontend process died. Check logs:${NC}"
        echo "  tail -f $SCRIPT_DIR/frontend.log"
        exit 1
    fi
    echo -n "."
    sleep 2
done

echo ""
echo -e "${YELLOW}Frontend is starting but may need more time.${NC}"
echo -e "Check status: curl http://localhost:3000"
echo -e "Check logs: tail -f $SCRIPT_DIR/frontend.log"
echo ""
echo -e "${GREEN}Frontend should be available at http://localhost:3000${NC}"
