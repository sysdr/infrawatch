#!/bin/bash

# Start Infrastructure Integration Testing System services

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "Starting Infrastructure Integration System"
echo "=========================================="
echo ""

# Check if services are already running
BACKEND_RUNNING=false
FRONTEND_RUNNING=false

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    BACKEND_RUNNING=true
    echo -e "${YELLOW}Backend is already running on port 8000${NC}"
else
    echo "Starting backend..."
    BACKEND_DIR="$SCRIPT_DIR/backend"
    cd "$BACKEND_DIR"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo -e "${RED}Error: Backend virtual environment not found. Please run ./build.sh first.${NC}"
        exit 1
    fi
    
    source venv/bin/activate
    
    # Check if requirements are installed
    if ! python3 -c "import fastapi" 2>/dev/null; then
        echo "Installing backend dependencies..."
        pip install -q -r requirements.txt
    fi
    
    echo "Starting backend server..."
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$SCRIPT_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$SCRIPT_DIR/backend.pid"
    echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
    cd "$SCRIPT_DIR"
fi

# Start frontend (via Docker for reliable startup; local node_modules often broken on WSL)
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    FRONTEND_RUNNING=true
    echo -e "${YELLOW}Frontend is already running on port 3000${NC}"
else
    echo "Starting frontend (Docker)..."
    cd "$SCRIPT_DIR"
    # Stop any local frontend process
    pkill -f "react-scripts start" 2>/dev/null || true
    docker compose stop frontend 2>/dev/null || true
    sleep 2
    # Run only frontend container (backend stays local)
    if docker compose up -d --no-deps --build frontend 2>&1; then
        echo -e "${GREEN}✓ Frontend container started${NC}"
        echo -e "${YELLOW}  Frontend serves static build; ready in seconds. Logs: docker compose logs -f frontend${NC}"
    else
        echo -e "${RED}Docker frontend failed. Falling back to local npm start...${NC}"
        FRONTEND_DIR="$SCRIPT_DIR/frontend"
        cd "$FRONTEND_DIR"
        [ ! -d "node_modules" ] && npm install --silent
        chmod +x node_modules/.bin/* 2>/dev/null || true
        BROWSER=none nohup npm start > "$SCRIPT_DIR/frontend.log" 2>&1 &
        echo $! > "$SCRIPT_DIR/frontend.pid"
        echo -e "${GREEN}✓ Frontend started locally (PID: $(cat $SCRIPT_DIR/frontend.pid))${NC}"
        cd "$SCRIPT_DIR"
    fi
fi

# Wait for services to be ready
echo ""
echo "Waiting for services to be ready..."
sleep 5

# Poll for frontend when we just started it (Docker compile can take 1–2 min)
if [ "$FRONTEND_RUNNING" = false ]; then
    echo -n "Waiting for frontend"
    for i in $(seq 1 24); do
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null | grep -q "200"; then
            echo ""
            break
        fi
        echo -n "."
        sleep 5
    done
    echo ""
fi

# Check service status
echo ""
echo -e "${GREEN}=== Service Status ===${NC}"

# Check backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend: http://localhost:8000${NC}"
else
    if [ "$BACKEND_RUNNING" = false ]; then
        echo -e "${YELLOW}⚠ Backend: Starting (check backend.log for details)${NC}"
    else
        echo -e "${RED}✗ Backend: Not responding${NC}"
    fi
fi

# Check frontend
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null | grep -q "200"; then
    echo -e "${GREEN}✓ Frontend: http://localhost:3000${NC}"
else
    if [ "$FRONTEND_RUNNING" = false ]; then
        echo -e "${YELLOW}⚠ Frontend: Starting (Docker: docker compose logs -f frontend | Local: tail -f frontend.log)${NC}"
    else
        echo -e "${RED}✗ Frontend: Not responding${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Services started!${NC}"
echo ""
echo "Access the application:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "View logs:"
echo "  tail -f backend.log"
echo "  tail -f frontend.log"
echo ""
echo "Stop services:"
echo "  ./stop.sh"
