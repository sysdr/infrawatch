#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================="
echo "Starting Cloud Provider API System"
echo "=================================="

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check for existing services
BACKEND_RUNNING=false
FRONTEND_RUNNING=false

if check_port 8000; then
    if pgrep -f "uvicorn.*app.main:app" > /dev/null; then
        echo "✓ Backend is already running on port 8000"
        BACKEND_RUNNING=true
    else
        echo "WARNING: Port 8000 is in use by another process"
    fi
fi

if check_port 3000; then
    if pgrep -f "react-scripts start" > /dev/null; then
        echo "✓ Frontend is already running on port 3000"
        FRONTEND_RUNNING=true
    else
        echo "WARNING: Port 3000 is in use by another process"
    fi
fi

# Start backend if not running
if [ "$BACKEND_RUNNING" = false ]; then
    echo "Starting backend..."
    BACKEND_DIR="$SCRIPT_DIR/backend"
    
    if [ ! -d "$BACKEND_DIR" ]; then
        echo "ERROR: Backend directory not found at $BACKEND_DIR"
        exit 1
    fi
    
    cd "$BACKEND_DIR"
    
    # Check if venv exists
    if [ ! -d "venv" ]; then
        echo "ERROR: Virtual environment not found. Run build.sh first."
        exit 1
    fi
    
    # Activate venv
    source venv/bin/activate
    
    echo "Starting backend server..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!
    sleep 3
    
    # Verify backend started
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "ERROR: Backend failed to start. Check /tmp/backend.log"
        exit 1
    fi
    
    echo $BACKEND_PID > "$SCRIPT_DIR/.backend.pid"
    echo "✓ Backend started (PID: $BACKEND_PID)"
    cd "$SCRIPT_DIR"
fi

# Start frontend if not running
if [ "$FRONTEND_RUNNING" = false ]; then
    echo "Starting frontend..."
    FRONTEND_DIR="$SCRIPT_DIR/frontend"
    
    if [ ! -d "$FRONTEND_DIR" ]; then
        echo "ERROR: Frontend directory not found at $FRONTEND_DIR"
        exit 1
    fi
    
    cd "$FRONTEND_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "ERROR: node_modules not found. Run build.sh first."
        exit 1
    fi
    
    echo "Starting frontend server..."
    npm start > /tmp/frontend.log 2>&1 &
    FRONTEND_PID=$!
    sleep 5
    
    # Verify frontend started
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "ERROR: Frontend failed to start. Check /tmp/frontend.log"
        exit 1
    fi
    
    echo $FRONTEND_PID > "$SCRIPT_DIR/.frontend.pid"
    echo "✓ Frontend started (PID: $FRONTEND_PID)"
    cd "$SCRIPT_DIR"
fi

echo ""
echo "=================================="
echo "✓ Services are running"
echo "=================================="
echo ""
echo "Access the application:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo ""
if [ "$BACKEND_RUNNING" = false ] || [ "$FRONTEND_RUNNING" = false ]; then
    echo "Logs:"
    [ "$BACKEND_RUNNING" = false ] && echo "  Backend: /tmp/backend.log"
    [ "$FRONTEND_RUNNING" = false ] && echo "  Frontend: /tmp/frontend.log"
    echo ""
fi
