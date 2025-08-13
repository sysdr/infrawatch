#!/bin/bash

echo "🛑 Stopping Server Management Integration System"
echo "==============================================="

# Stop backend
if [ -f "backend/backend.pid" ]; then
    BACKEND_PID=$(cat backend/backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        kill $BACKEND_PID
        echo "✅ Backend server stopped"
    fi
    rm -f backend/backend.pid
fi

# Stop frontend
if [ -f "frontend/frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        kill $FRONTEND_PID
        echo "✅ Frontend server stopped"
    fi
    rm -f frontend/frontend.pid
fi

# Kill any remaining processes
pkill -f "uvicorn app.main:app"
pkill -f "npm start"

echo "🏁 System shutdown complete"
