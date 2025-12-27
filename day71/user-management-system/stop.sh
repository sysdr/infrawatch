#!/bin/bash

MODE=${1:-no-docker}

if [ "$MODE" = "docker" ]; then
    cd docker
    docker-compose down
else
    pkill -f "uvicorn app.main:app"
    pkill -f "vite"
fi

echo "✓ System stopped"
