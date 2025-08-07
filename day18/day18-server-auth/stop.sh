#!/bin/bash

echo "🛑 Stopping Server Authentication System"
echo "======================================="

# Kill backend process
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    echo "Stopping backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null
    rm .backend.pid
fi

# Kill frontend process
if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    echo "Stopping frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null
    rm .frontend.pid
fi

# Kill any remaining processes
pkill -f "uvicorn.*main:app" 2>/dev/null
pkill -f "react-scripts start" 2>/dev/null

echo "✅ All services stopped"
