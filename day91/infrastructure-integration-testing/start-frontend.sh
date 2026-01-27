#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

FRONTEND_DIR="$SCRIPT_DIR/frontend"
cd "$FRONTEND_DIR"

echo -e "${GREEN}Starting Frontend Server...${NC}"

# Wait for npm install to complete if it's running
if pgrep -f "npm install" > /dev/null; then
    echo -e "${YELLOW}Waiting for npm install to complete...${NC}"
    while pgrep -f "npm install" > /dev/null; do
        sleep 2
    done
    echo -e "${GREEN}npm install completed${NC}"
fi

# Ensure dependencies are installed
if [ ! -d "node_modules" ] || [ ! -f "node_modules/.bin/react-scripts" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
fi

# Fix permissions on node_modules binaries
echo -e "${GREEN}Fixing permissions...${NC}"
if [ -d "node_modules/.bin" ]; then
    chmod +x node_modules/.bin/* 2>/dev/null || true
fi

# Check if frontend is already running
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}Port 3000 is already in use. Stopping existing process...${NC}"
    pkill -f "react-scripts start" || true
    sleep 2
fi

# Start frontend server
echo -e "${GREEN}Starting frontend server on port 3000...${NC}"
nohup npm start > "$SCRIPT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$SCRIPT_DIR/frontend.pid"

echo -e "${GREEN}Frontend server started (PID: $FRONTEND_PID)${NC}"
echo "Waiting for server to be ready..."
sleep 10

# Check if server is responding
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}Frontend is running at http://localhost:3000${NC}"
else
    echo -e "${YELLOW}Frontend may still be starting. Check logs: tail -f $SCRIPT_DIR/frontend.log${NC}"
fi
