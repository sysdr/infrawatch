#!/bin/bash

echo "🛑 Stopping Task Monitoring System"
echo "=================================="

# Check if running with Docker
if docker-compose ps | grep -q "Up"; then
    echo "🐳 Stopping Docker containers..."
    docker-compose down
    echo "✅ Docker containers stopped"
    exit 0
fi

# Stop local processes
if [ -f backend.pid ]; then
    BACKEND_PID=$(cat backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🐍 Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
    fi
    rm -f backend.pid
fi

if [ -f frontend.pid ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "⚛️ Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
    fi
    rm -f frontend.pid
fi

# Kill any remaining processes on ports
echo "🧹 Cleaning up remaining processes..."
lsof -ti:8000 | xargs -r kill -9 2>/dev/null || true
lsof -ti:3000 | xargs -r kill -9 2>/dev/null || true

echo "✅ All services stopped"
