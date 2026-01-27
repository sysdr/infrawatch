#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

cd "$FRONTEND_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Monitoring npm install and starting frontend...${NC}"

# Wait for npm install
while pgrep -f "npm install" > /dev/null; do
    SIZE=$(du -sh node_modules 2>/dev/null | cut -f1)
    echo -e "${YELLOW}npm install in progress... (node_modules: $SIZE)${NC}"
    sleep 5
done

echo -e "${GREEN}npm install completed!${NC}"

# Wait a bit more for files to settle
sleep 3

# Verify critical dependencies
if [ ! -f "node_modules/.bin/react-scripts" ] || [ ! -d "node_modules/@mui/material" ]; then
    echo -e "${YELLOW}Dependencies incomplete. Running npm install...${NC}"
    npm install
fi

# Fix permissions
chmod +x node_modules/.bin/* 2>/dev/null || true

# Stop existing frontend
pkill -f "react-scripts start" 2>/dev/null || true
pkill -f "npm.*start" 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 2

# Start frontend
echo -e "${GREEN}Starting frontend...${NC}"
BROWSER=none nohup npm start > "$SCRIPT_DIR/frontend.log" 2>&1 &
echo $! > "$SCRIPT_DIR/frontend.pid"

echo -e "${GREEN}Frontend starting. Monitor with: tail -f $SCRIPT_DIR/frontend.log${NC}"
echo -e "${GREEN}Access at: http://localhost:3000${NC}"
