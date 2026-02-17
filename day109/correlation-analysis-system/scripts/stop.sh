#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Stopping all services..."

# Kill backend
pkill -f "uvicorn main:app" 2>/dev/null || true

# Kill frontend
pkill -f "react-scripts start" 2>/dev/null || true

# Stop Docker if running
if [ -d "$PROJECT_ROOT/docker" ]; then
  cd "$PROJECT_ROOT/docker"
  docker-compose down 2>/dev/null || true
fi

echo "All services stopped."
