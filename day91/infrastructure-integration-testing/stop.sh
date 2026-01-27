#!/bin/bash

echo "Stopping Infrastructure Integration System..."

if [ -f "backend.pid" ]; then
    kill $(cat backend.pid) 2>/dev/null || true
    rm backend.pid
fi

if [ -f "frontend.pid" ]; then
    kill $(cat frontend.pid) 2>/dev/null || true
    rm frontend.pid
fi

# Stop Docker services if running
docker-compose down 2>/dev/null || true

echo "Services stopped"
