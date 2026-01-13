#!/bin/bash

echo "Stopping Security Assessment Platform..."

if [ -f "backend.pid" ] && [ -f "frontend.pid" ]; then
    # Stop local services
    kill $(cat backend.pid) 2>/dev/null
    kill $(cat frontend.pid) 2>/dev/null
    rm backend.pid frontend.pid
    echo "Local services stopped"
else
    # Stop Docker services
    docker-compose down
    echo "Docker services stopped"
fi
