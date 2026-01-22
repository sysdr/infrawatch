#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Stopping Cloud Provider API System..."

DOCKER_DIR="$SCRIPT_DIR/docker"
DOCKER_COMPOSE_FILE="$DOCKER_DIR/docker-compose.yml"

if [ -f "$DOCKER_COMPOSE_FILE" ] && docker-compose -f "$DOCKER_COMPOSE_FILE" ps 2>/dev/null | grep -q "Up"; then
    echo "Stopping Docker containers..."
    cd "$DOCKER_DIR"
    docker-compose down
    cd "$SCRIPT_DIR"
else
    echo "Stopping local processes..."
    
    # Stop backend
    BACKEND_PID_FILE="$SCRIPT_DIR/.backend.pid"
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            echo "Stopping backend (PID: $BACKEND_PID)..."
            kill "$BACKEND_PID" 2>/dev/null
            sleep 2
            # Force kill if still running
            if kill -0 "$BACKEND_PID" 2>/dev/null; then
                kill -9 "$BACKEND_PID" 2>/dev/null
            fi
        fi
        rm -f "$BACKEND_PID_FILE"
    fi
    
    # Also kill any uvicorn processes
    pkill -f "uvicorn.*app.main:app" 2>/dev/null
    
    # Stop frontend
    FRONTEND_PID_FILE="$SCRIPT_DIR/.frontend.pid"
    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            echo "Stopping frontend (PID: $FRONTEND_PID)..."
            kill "$FRONTEND_PID" 2>/dev/null
            sleep 2
            # Force kill if still running
            if kill -0 "$FRONTEND_PID" 2>/dev/null; then
                kill -9 "$FRONTEND_PID" 2>/dev/null
            fi
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi
    
    # Also kill any react-scripts processes
    pkill -f "react-scripts start" 2>/dev/null
fi

echo "✓ Services stopped"
