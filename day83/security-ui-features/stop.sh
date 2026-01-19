#!/bin/bash

echo "Stopping Security UI Features services..."

if [ "$1" == "--docker" ]; then
    cd docker
    docker-compose down
    echo "Docker services stopped."
else
    # Stop local services
    if [ -f backend.pid ]; then
        kill $(cat backend.pid) 2>/dev/null || true
        rm backend.pid
        echo "Backend stopped."
    fi
    
    if [ -f frontend.pid ]; then
        kill $(cat frontend.pid) 2>/dev/null || true
        rm frontend.pid
        echo "Frontend stopped."
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "react-scripts start" 2>/dev/null || true
    
    echo "All services stopped."
fi
