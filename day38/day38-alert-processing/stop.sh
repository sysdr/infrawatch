#!/bin/bash

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🛑 Stopping Alert Processing Pipeline..."

# Kill backend
if [ -f "$SCRIPT_DIR/.backend.pid" ]; then
    BACKEND_PID=$(cat "$SCRIPT_DIR/.backend.pid")
    kill $BACKEND_PID 2>/dev/null
    rm "$SCRIPT_DIR/.backend.pid"
    echo "🔧 Backend stopped"
fi

# Kill frontend  
if [ -f "$SCRIPT_DIR/.frontend.pid" ]; then
    FRONTEND_PID=$(cat "$SCRIPT_DIR/.frontend.pid")
    kill $FRONTEND_PID 2>/dev/null
    rm "$SCRIPT_DIR/.frontend.pid"
    echo "🎨 Frontend stopped"
fi

# Kill any remaining processes
pkill -f "python -m app.main" 2>/dev/null
pkill -f "npm start" 2>/dev/null
pkill -f "react-scripts start" 2>/dev/null

echo "✅ All services stopped"
