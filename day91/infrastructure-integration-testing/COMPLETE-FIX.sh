#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Complete Frontend Fix${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

cd "$FRONTEND_DIR"

# Step 1: Wait for npm install
echo -e "${YELLOW}Step 1: Waiting for npm install to complete...${NC}"
while pgrep -f "npm install" > /dev/null; do
    SIZE=$(du -sh node_modules 2>/dev/null | cut -f1 || echo "0")
    echo -e "  npm install in progress... (node_modules: $SIZE)"
    sleep 5
done
echo -e "${GREEN}✓ npm install completed${NC}"
echo ""

# Step 2: Verify dependencies
echo -e "${YELLOW}Step 2: Verifying dependencies...${NC}"
if [ ! -f "node_modules/.bin/react-scripts" ]; then
    echo -e "${RED}✗ react-scripts not found. Running npm install...${NC}"
    npm install
fi

if [ ! -d "node_modules/@mui/material" ]; then
    echo -e "${RED}✗ @mui/material not found. Running npm install...${NC}"
    npm install
fi

echo -e "${GREEN}✓ Dependencies verified${NC}"
echo ""

# Step 3: Fix permissions
echo -e "${YELLOW}Step 3: Fixing permissions...${NC}"
if [ -d "node_modules/.bin" ]; then
    find node_modules/.bin -type f -exec chmod +x {} \; 2>/dev/null || true
fi
echo -e "${GREEN}✓ Permissions fixed${NC}"
echo ""

# Step 4: Stop existing processes
echo -e "${YELLOW}Step 4: Stopping existing frontend processes...${NC}"
pkill -f "react-scripts start" 2>/dev/null || true
pkill -f "npm.*start" 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 2
echo -e "${GREEN}✓ Processes stopped${NC}"
echo ""

# Step 5: Start frontend
echo -e "${YELLOW}Step 5: Starting frontend server...${NC}"
cd "$FRONTEND_DIR"
BROWSER=none PORT=3000 nohup npm start > "$SCRIPT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$SCRIPT_DIR/frontend.pid"
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo ""

# Step 6: Wait for compilation
echo -e "${YELLOW}Step 6: Waiting for compilation (this may take 30-60 seconds)...${NC}"
for i in {1..40}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}✅ SUCCESS! Frontend is now running!${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo ""
        echo -e "Access your application at:"
        echo -e "  ${GREEN}Frontend: http://localhost:3000${NC}"
        echo -e "  ${GREEN}Backend:  http://localhost:8000${NC}"
        echo -e "  ${GREEN}API Docs:  http://localhost:8000/docs${NC}"
        echo ""
        exit 0
    fi
    
    # Check if process died
    if ! ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo ""
        echo -e "${RED}✗ Frontend process died. Check logs:${NC}"
        echo "  tail -f $SCRIPT_DIR/frontend.log"
        exit 1
    fi
    
    echo -n "."
    sleep 2
done

echo ""
echo -e "${YELLOW}Frontend is still compiling. Check status:${NC}"
echo "  curl http://localhost:3000"
echo "  tail -f $SCRIPT_DIR/frontend.log"
echo ""
echo -e "${GREEN}Frontend should be available soon at http://localhost:3000${NC}"
