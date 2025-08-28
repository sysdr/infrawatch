#!/bin/bash

echo "🛑 Stopping Metrics Aggregation System"

# Check if Docker Compose is running
if docker-compose ps | grep -q "Up"; then
    echo "📦 Stopping Docker services..."
    docker-compose down
else
    echo "🐍 Stopping development services..."
    
    # Kill backend
    if [ -f ".backend.pid" ]; then
        BACKEND_PID=$(cat .backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            echo "✅ Backend stopped"
        fi
        rm .backend.pid
    fi
    
    # Kill frontend
    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            echo "✅ Frontend stopped"
        fi
        rm .frontend.pid
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn.*app.main:app" || true
    pkill -f "react-scripts start" || true
fi

echo "🎉 System stopped successfully!"
