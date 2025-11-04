#!/bin/bash

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🛑 Stopping Notification UI System..."

# Kill backend
if [ -f "$SCRIPT_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat "$SCRIPT_DIR/backend.pid")
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend stopped (PID: $BACKEND_PID)"
    fi
    rm -f "$SCRIPT_DIR/backend.pid"
fi

# Kill frontend
if [ -f "$SCRIPT_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$SCRIPT_DIR/frontend.pid")
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Frontend stopped (PID: $FRONTEND_PID)"
    fi
    rm -f "$SCRIPT_DIR/frontend.pid"
fi

# Kill any remaining processes by name
if pgrep -f "uvicorn.*app.main:app" > /dev/null; then
    pkill -f "uvicorn.*app.main:app"
    echo "✅ Cleaned up remaining uvicorn processes"
fi

if pgrep -f "vite" > /dev/null; then
    pkill -f "vite"
    echo "✅ Cleaned up remaining vite processes"
fi

echo "✅ System stopped"
