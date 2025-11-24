#!/bin/bash

echo "Stopping services..."

if [ -f "docker-compose.yml" ] && docker-compose ps | grep -q "Up"; then
    echo "Stopping Docker containers..."
    docker-compose down
else
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
    pkill -f "vite" || true
fi

echo "Services stopped."
