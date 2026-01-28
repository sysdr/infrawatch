#!/bin/bash

echo "Stopping Log Aggregation System..."

if [ "$1" == "--docker" ]; then
    cd docker
    docker-compose down
    echo "Docker services stopped"
    exit 0
fi

# Stop non-Docker services
if [ -f .backend.pid ]; then
    kill $(cat .backend.pid) 2>/dev/null || true
    rm .backend.pid
fi

if [ -f .shipper.pid ]; then
    kill $(cat .shipper.pid) 2>/dev/null || true
    rm .shipper.pid
fi

if [ -f .frontend.pid ]; then
    kill $(cat .frontend.pid) 2>/dev/null || true
    rm .frontend.pid
fi

# Kill any remaining processes
pkill -f "uvicorn" || true
pkill -f "shipper.py" || true
pkill -f "react-scripts" || true

echo "All services stopped"
