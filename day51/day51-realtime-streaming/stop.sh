#!/bin/bash

echo "Stopping services..."

if [ "$1" == "--docker" ]; then
    docker-compose down
    echo "Docker services stopped"
else
    if [ -f backend.pid ]; then
        kill $(cat backend.pid) 2>/dev/null || true
        rm backend.pid
    fi
    
    if [ -f frontend.pid ]; then
        kill $(cat frontend.pid) 2>/dev/null || true
        rm frontend.pid
    fi
    
    # Cleanup any remaining processes
    pkill -f "uvicorn app.main" || true
    pkill -f "vite" || true
    
    echo "Services stopped"
fi
