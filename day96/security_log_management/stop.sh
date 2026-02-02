#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Stopping Security Log Management System..."

if [ "$1" == "--docker" ]; then
    cd "$SCRIPT_DIR/docker"
    docker-compose down
    echo "Docker services stopped"
    exit 0
fi

# Stop local services (avoid duplicate: only kill if PID file exists)
if [ -f "$SCRIPT_DIR/.backend.pid" ]; then
    kill $(cat "$SCRIPT_DIR/.backend.pid") 2>/dev/null
    rm -f "$SCRIPT_DIR/.backend.pid"
    echo "Backend stopped"
fi

if [ -f "$SCRIPT_DIR/.frontend.pid" ]; then
    kill $(cat "$SCRIPT_DIR/.frontend.pid") 2>/dev/null
    rm -f "$SCRIPT_DIR/.frontend.pid"
    echo "Frontend stopped"
fi

echo "All services stopped"
