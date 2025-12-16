#!/bin/bash

echo "Stopping Dashboard Customization System..."

PROJECT_ROOT=$(cd "$(dirname "$0")" && pwd)

if [ -f "$PROJECT_ROOT/docker-compose.yml" ] && command -v docker-compose >/dev/null 2>&1; then
    cd "$PROJECT_ROOT"
    docker-compose down
    echo "✓ Docker containers stopped"
else
    # Stop backend
    if [ -f "$PROJECT_ROOT/backend.pid" ]; then
        BACKEND_PID=$(cat "$PROJECT_ROOT/backend.pid")
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            kill $BACKEND_PID 2>/dev/null || true
        fi
        rm -f "$PROJECT_ROOT/backend.pid"
    fi
    
    # Also kill any remaining uvicorn processes
    pkill -f "uvicorn.*app.main" 2>/dev/null || true
    
    # Stop frontend
    if [ -f "$PROJECT_ROOT/frontend.pid" ]; then
        FRONTEND_PID=$(cat "$PROJECT_ROOT/frontend.pid")
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            kill $FRONTEND_PID 2>/dev/null || true
        fi
        rm -f "$PROJECT_ROOT/frontend.pid"
    fi
    
    # Also kill any remaining react/node processes
    pkill -f "react-scripts start" 2>/dev/null || true
    
    echo "✓ Services stopped"
fi
