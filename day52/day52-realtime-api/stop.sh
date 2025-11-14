#!/bin/bash

# Get the absolute path of the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "Stopping services..."

if [ -f "$PROJECT_ROOT/.backend.pid" ]; then
    PID=$(cat "$PROJECT_ROOT/.backend.pid")
    if kill -0 $PID 2>/dev/null; then
        kill $PID 2>/dev/null || true
        echo "Stopped backend (PID: $PID)"
    fi
    rm "$PROJECT_ROOT/.backend.pid"
fi

if [ -f "$PROJECT_ROOT/.frontend.pid" ]; then
    PID=$(cat "$PROJECT_ROOT/.frontend.pid")
    if kill -0 $PID 2>/dev/null; then
        kill $PID 2>/dev/null || true
        echo "Stopped frontend (PID: $PID)"
    fi
    rm "$PROJECT_ROOT/.frontend.pid"
fi

# Kill any remaining processes
pkill -f "uvicorn app.main:app" || true
pkill -f "vite" || true

echo "All services stopped"
