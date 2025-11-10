#!/bin/bash

echo "Stopping WebSocket Infrastructure..."

if [ -f "backend.pid" ]; then
    PID=$(cat backend.pid)
    kill $PID 2>/dev/null || true
    rm backend.pid
    echo "Backend stopped"
fi

if [ -f "frontend.pid" ]; then
    PID=$(cat frontend.pid)
    kill $PID 2>/dev/null || true
    rm frontend.pid
    echo "Frontend stopped"
fi

# Stop Docker if running
docker-compose down 2>/dev/null || true

echo "✅ All services stopped"
