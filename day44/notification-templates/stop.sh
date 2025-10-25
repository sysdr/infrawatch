#!/bin/bash

echo "🛑 Stopping Notification Templates System"

if command -v docker &> /dev/null && [ -f "docker-compose.yml" ]; then
    echo "🐳 Stopping Docker containers..."
    docker-compose down
else
    echo "📦 Stopping local services..."
    
    if [ -f ".backend.pid" ]; then
        BACKEND_PID=$(cat .backend.pid)
        kill $BACKEND_PID 2>/dev/null || true
        rm .backend.pid
    fi
    
    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        kill $FRONTEND_PID 2>/dev/null || true
        rm .frontend.pid
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn app.main:app" || true
    pkill -f "npm start" || true
fi

echo "✅ All services stopped"
