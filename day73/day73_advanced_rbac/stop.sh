#!/bin/bash

# Get absolute path of script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "🛑 Stopping Advanced RBAC System..."

# Stop Docker services if running
if docker-compose -f "$PROJECT_ROOT/docker-compose.yml" ps | grep -q "Up"; then
    echo "Stopping Docker services..."
    cd "$PROJECT_ROOT" || exit 1
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" down
fi

# Kill backend and frontend processes
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo "Stopping backend service..."
    pkill -f "uvicorn app.main:app"
fi

if pgrep -f "react-scripts start" > /dev/null; then
    echo "Stopping frontend service..."
    pkill -f "react-scripts start"
fi

echo "✅ System stopped"
