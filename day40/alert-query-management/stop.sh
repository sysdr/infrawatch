#!/bin/bash

echo "🛑 Stopping Alert Query & Management System..."

# Stop backend
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        kill $BACKEND_PID
        echo "🐍 Backend stopped"
    fi
    rm .backend.pid
fi

# Stop frontend
if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        kill $FRONTEND_PID
        echo "⚛️ Frontend stopped"
    fi
    rm .frontend.pid
fi

# Kill any remaining processes
pkill -f "uvicorn app.main:app"
pkill -f "npm start"

echo "✅ All services stopped"
