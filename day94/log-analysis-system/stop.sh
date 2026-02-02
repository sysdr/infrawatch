#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STOP_TYPE=${1:-local}

if [ "$STOP_TYPE" == "docker" ]; then
    echo "Stopping Docker containers..."
    (cd "$SCRIPT_DIR" && docker-compose down)
else
    echo "Stopping local services..."
    [ -f "$SCRIPT_DIR/.backend.pid" ] && kill $(cat "$SCRIPT_DIR/.backend.pid") 2>/dev/null || true
    [ -f "$SCRIPT_DIR/.backend.pid" ] && rm -f "$SCRIPT_DIR/.backend.pid"
    [ -f "$SCRIPT_DIR/.frontend.pid" ] && kill $(cat "$SCRIPT_DIR/.frontend.pid") 2>/dev/null || true
    [ -f "$SCRIPT_DIR/.frontend.pid" ] && rm -f "$SCRIPT_DIR/.frontend.pid"
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "react-scripts start" 2>/dev/null || true
fi

echo "✅ Services stopped"
