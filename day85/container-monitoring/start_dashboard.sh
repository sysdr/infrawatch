#!/bin/bash

# Start script for Container Monitoring Dashboard

set -e

echo "============================================"
echo "Starting Container Monitoring Dashboard"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}Warning: Docker is not running. Some features may not work.${NC}"
    echo ""
fi

# Start backend
echo -e "${BLUE}Starting Backend Server...${NC}"

# Ensure we're in the container-monitoring directory
cd "$(dirname "$0")"

if [ ! -d "backend/venv" ]; then
    echo "Creating virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt > /dev/null 2>&1
    cd ..
else
    source backend/venv/bin/activate
fi

if [ ! -f "backend/venv/bin/uvicorn" ]; then
    echo "Installing dependencies..."
    cd backend
    pip install -r requirements.txt > /dev/null 2>&1
    cd ..
fi

echo "Backend starting on http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""

# Start backend in background - MUST run from container-monitoring directory
cd "$(dirname "$0")"
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend
echo -e "${BLUE}Starting Frontend Server...${NC}"
cd "$(dirname "$0")/frontend"

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install > /dev/null 2>&1
fi

echo "Frontend starting on http://localhost:3000"
echo ""

# Start frontend
cd "$(dirname "$0")/frontend"
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}============================================"
echo "Dashboard is starting!"
echo "============================================${NC}"
echo ""
echo -e "${GREEN}Backend:${NC}  http://localhost:8000"
echo -e "${GREEN}API Docs:${NC} http://localhost:8000/docs"
echo -e "${GREEN}Frontend:${NC} http://localhost:3000 (check terminal for actual port)"
echo ""
echo "Logs:"
echo "  Backend:  tail -f backend.log"
echo "  Frontend: tail -f frontend.log"
echo ""
echo "To stop:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for user interrupt
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

wait
