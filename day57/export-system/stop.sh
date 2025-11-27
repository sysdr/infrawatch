#!/bin/bash

USE_DOCKER=${1:-"no-docker"}

if [ "$USE_DOCKER" == "docker" ]; then
    echo "🛑 Stopping Docker services..."
    docker-compose down
else
    echo "🛑 Stopping services..."
    
    # Stop frontend
    if [ -f frontend/frontend.pid ]; then
        kill $(cat frontend/frontend.pid) 2>/dev/null || true
        rm frontend/frontend.pid
    fi
    
    # Stop backend
    if [ -f backend/backend.pid ]; then
        kill $(cat backend/backend.pid) 2>/dev/null || true
        rm backend/backend.pid
    fi
    
    # Stop Celery
    if [ -f backend/celery.pid ]; then
        kill $(cat backend/celery.pid) 2>/dev/null || true
        rm backend/celery.pid
    fi
    
    echo "✅ All services stopped"
fi
