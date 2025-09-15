#!/bin/bash

echo "🛑 Stopping Task Orchestration System..."

# Kill backend
if [ -f backend.pid ]; then
    BACKEND_PID=$(cat backend.pid)
    kill $BACKEND_PID 2>/dev/null || true
    rm backend.pid
fi

# Kill frontend  
if [ -f frontend.pid ]; then
    FRONTEND_PID=$(cat frontend.pid)
    kill $FRONTEND_PID 2>/dev/null || true
    rm frontend.pid
fi

# Kill any remaining processes
pkill -f "python main.py" || true
pkill -f "npm start" || true
pkill -f "react-scripts start" || true

echo "✅ Services stopped"
