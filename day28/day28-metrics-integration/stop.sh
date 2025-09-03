#!/bin/bash

echo "🛑 Stopping Day 28: Metrics System Integration"

# Stop frontend
if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    echo "Stopping frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null || true
    rm .frontend.pid
fi

# Stop backend
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    echo "Stopping backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || true
    rm .backend.pid
fi

# Stop Docker services
echo "🐳 Stopping infrastructure services..."
docker-compose down

# Deactivate virtual environment
deactivate 2>/dev/null || true

echo "✅ All services stopped"
