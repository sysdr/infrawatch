#!/bin/bash

echo "=========================================="
echo "Stopping Real-time Performance System"
echo "=========================================="

if [ -f "docker/docker-compose.yml" ] && [ "$(docker-compose -f docker/docker-compose.yml ps -q)" ]; then
    echo "Stopping Docker containers..."
    cd docker
    docker-compose down
    cd ..
else
    echo "Stopping local services..."
    
    if [ -f "backend.pid" ]; then
        kill $(cat backend.pid) 2>/dev/null || true
        rm backend.pid
    fi
    
    if [ -f "frontend.pid" ]; then
        kill $(cat frontend.pid) 2>/dev/null || true
        rm frontend.pid
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn app.main:app" || true
    pkill -f "react-scripts start" || true
fi

echo "=========================================="
echo "Services Stopped"
echo "=========================================="
