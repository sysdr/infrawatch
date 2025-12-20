#!/bin/bash

# Get absolute path of script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Stopping services..."

if [ -f "$SCRIPT_DIR/backend/backend.pid" ]; then
    kill $(cat "$SCRIPT_DIR/backend/backend.pid") 2>/dev/null || true
    rm "$SCRIPT_DIR/backend/backend.pid"
fi

if [ -f "$SCRIPT_DIR/frontend/frontend.pid" ]; then
    kill $(cat "$SCRIPT_DIR/frontend/frontend.pid") 2>/dev/null || true
    rm "$SCRIPT_DIR/frontend/frontend.pid"
fi

# Kill any remaining processes
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

echo "Services stopped."
