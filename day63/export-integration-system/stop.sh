#!/bin/bash

PROJECT_DIR="/home/systemdr/git/infrawatch/day63/export-integration-system"

echo "Stopping Export Integration System..."

if command -v docker &> /dev/null; then
    cd "$PROJECT_DIR/docker"
    docker-compose down
else
    pkill -f uvicorn || true
    pkill -f celery || true
    pkill -f "react-scripts" || true
fi

echo "✅ System stopped"
