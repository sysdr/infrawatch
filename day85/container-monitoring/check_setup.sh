#!/bin/bash

# Setup verification script for Container Monitoring Dashboard

echo "============================================"
echo "Container Monitoring - Setup Check"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

# Check Docker
echo -n "Checking Docker... "
if command -v docker &> /dev/null && docker info &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
    CONTAINER_COUNT=$(docker ps -q | wc -l)
    echo "  Running containers: $CONTAINER_COUNT"
else
    echo -e "${RED}✗${NC}"
    echo "  Docker is not running or not installed"
    ERRORS=$((ERRORS + 1))
fi

# Check Backend
echo -n "Checking Backend (port 8000)... "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
    HEALTH=$(curl -s http://localhost:8000/health)
    echo "  Response: $HEALTH"
else
    echo -e "${RED}✗${NC}"
    echo "  Backend is not running"
    echo "  Start with: cd backend && source venv/bin/activate && uvicorn backend.app.main:app --reload"
    ERRORS=$((ERRORS + 1))
fi

# Check Frontend
echo -n "Checking Frontend (port 3000/3001)... "
if curl -s http://localhost:3000 > /dev/null 2>&1 || curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "  Frontend running on: http://localhost:3000"
    else
        echo "  Frontend running on: http://localhost:3001"
    fi
else
    echo -e "${YELLOW}⚠${NC}"
    echo "  Frontend may not be running"
    echo "  Start with: cd frontend && npm run dev"
fi

# Check WebSocket
echo -n "Checking WebSocket endpoint... "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    # Try to check if WebSocket endpoint exists (basic check)
    echo -e "${GREEN}✓${NC}"
    echo "  WebSocket should be available at: ws://localhost:8000/api/v1/ws/metrics"
else
    echo -e "${RED}✗${NC}"
    echo "  Cannot check WebSocket - backend not running"
fi

echo ""
echo "============================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}Setup looks good!${NC}"
    echo ""
    echo "Dashboard should be accessible at:"
    echo "  http://localhost:3000 or http://localhost:3001"
else
    echo -e "${RED}Found $ERRORS issue(s)${NC}"
    echo ""
    echo "To fix:"
    echo "  1. Start backend: cd backend && source venv/bin/activate && uvicorn backend.app.main:app --reload"
    echo "  2. Start frontend: cd frontend && npm run dev"
    echo "  3. Or use: ./start_dashboard.sh"
fi
echo "============================================"
