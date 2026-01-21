#!/bin/bash

# Get the script directory (project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/backend"
FRONTEND_DIR="${SCRIPT_DIR}/frontend"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "============================================"
echo "Starting Container Monitoring System"
echo "============================================"
echo ""

# Check if services are already running
if pgrep -f "uvicorn.*backend.app.main" > /dev/null; then
    echo -e "${YELLOW}Warning: Backend service is already running${NC}"
else
    echo -e "${GREEN}Starting backend...${NC}"
    # Start backend in background
    cd "${SCRIPT_DIR}" || exit 1
    nohup bash run-backend.sh > backend.log 2>&1 &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"
    sleep 3
fi

# Check if frontend is already running
if pgrep -f "vite" > /dev/null; then
    echo -e "${YELLOW}Warning: Frontend service is already running${NC}"
else
    echo -e "${GREEN}Starting frontend...${NC}"
    # Start frontend in background
    cd "${SCRIPT_DIR}" || exit 1
    nohup bash start-frontend.sh > frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "Frontend started with PID: $FRONTEND_PID"
    sleep 3
fi

echo ""
echo "============================================"
echo "Services Status"
echo "============================================"
echo ""

# Check backend status
sleep 2
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend: Running on http://localhost:8000${NC}"
else
    echo -e "${RED}✗ Backend: Not responding (check backend.log)${NC}"
fi

# Check frontend status
FRONTEND_PORT=$(netstat -tlnp 2>/dev/null | grep -o ':300[0-9] ' | head -1 | tr -d ': ' || echo "3001")
if curl -s "http://localhost:${FRONTEND_PORT}" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend: Running on http://localhost:${FRONTEND_PORT}${NC}"
else
    echo -e "${YELLOW}⚠ Frontend: Starting (may take a few seconds)${NC}"
fi

echo ""
echo "============================================"
echo "Access URLs"
echo "============================================"
echo "Dashboard: http://localhost:${FRONTEND_PORT}"
echo "API:       http://localhost:8000"
echo "API Docs:  http://localhost:8000/docs"
echo ""
echo "Logs:"
echo "  Backend:  tail -f backend.log"
echo "  Frontend: tail -f frontend.log"
echo ""
echo "To stop: ./stop.sh"
echo ""
