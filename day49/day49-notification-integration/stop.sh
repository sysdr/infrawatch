#!/bin/bash

echo "Stopping services..."

# Stop Docker if running
if docker-compose ps 2>/dev/null | grep -q "Up"; then
    echo "Stopping Docker services..."
    docker-compose down
fi

# Stop local processes
if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null || true
    rm backend.pid
fi

if [ -f frontend.pid ]; then
    kill $(cat frontend.pid) 2>/dev/null || true
    rm frontend.pid
fi

echo "✓ All services stopped"
