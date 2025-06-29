#!/bin/bash

echo "🛑 Stopping RBAC System..."

# Stop Docker services if running
if [ -f "docker-compose.yml" ]; then
    docker-compose down
    echo "✅ Docker services stopped"
fi

# Kill any running uvicorn processes
pkill -f uvicorn || true

echo "✅ RBAC System stopped"
