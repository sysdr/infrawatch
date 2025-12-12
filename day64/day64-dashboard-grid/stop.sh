#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Stopping Dashboard Grid System..."

if [ -f "$SCRIPT_DIR/.backend.pid" ]; then
    BACKEND_PID=$(cat "$SCRIPT_DIR/.backend.pid")
    kill $BACKEND_PID 2>/dev/null || true
    rm "$SCRIPT_DIR/.backend.pid"
    echo "Backend stopped"
fi

if [ -f "$SCRIPT_DIR/.frontend.pid" ]; then
    FRONTEND_PID=$(cat "$SCRIPT_DIR/.frontend.pid")
    kill $FRONTEND_PID 2>/dev/null || true
    rm "$SCRIPT_DIR/.frontend.pid"
    echo "Frontend stopped"
fi

# Kill any remaining processes
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true

echo "All services stopped"
