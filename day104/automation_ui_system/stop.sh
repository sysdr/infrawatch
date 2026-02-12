#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    echo "Stopping Docker containers..."
    docker compose down
elif command -v docker &> /dev/null && docker-compose version &> /dev/null; then
    docker-compose down
else
    echo "Stopping local processes..."
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "celery.*app.workers.celery_app" 2>/dev/null || true
    pkill -f "react-scripts start" 2>/dev/null || true
fi

echo "All services stopped"
