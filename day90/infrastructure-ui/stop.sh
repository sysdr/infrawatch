#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo "Stopping Infrastructure UI services..."

# Check if running with Docker
if docker-compose ps >/dev/null 2>&1; then
    echo "Stopping Docker containers..."
    docker-compose down
    echo "✓ Docker services stopped"
else
    # Stop local processes by PID files
    if [ -f "$SCRIPT_DIR/.backend.pid" ]; then
        BACKEND_PID=$(cat "$SCRIPT_DIR/.backend.pid")
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            echo "✓ Backend stopped (PID: $BACKEND_PID)"
        fi
        rm "$SCRIPT_DIR/.backend.pid"
    fi
    
    if [ -f "$SCRIPT_DIR/.frontend.pid" ]; then
        FRONTEND_PID=$(cat "$SCRIPT_DIR/.frontend.pid")
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            echo "✓ Frontend stopped (PID: $FRONTEND_PID)"
        fi
        rm "$SCRIPT_DIR/.frontend.pid"
    fi
    
    # Also kill any remaining processes
    pkill -f "uvicorn.*8000" 2>/dev/null && echo "✓ Killed remaining backend processes"
    pkill -f "vite.*5173" 2>/dev/null && echo "✓ Killed remaining frontend processes"
fi

echo "All services stopped"
