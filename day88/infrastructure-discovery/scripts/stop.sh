#!/bin/bash

echo "Stopping Infrastructure Discovery System..."

# Stop backend
if [ -f /tmp/discovery_backend.pid ]; then
    kill $(cat /tmp/discovery_backend.pid) 2>/dev/null
    rm /tmp/discovery_backend.pid
fi

# Stop frontend
if [ -f /tmp/discovery_frontend.pid ]; then
    kill $(cat /tmp/discovery_frontend.pid) 2>/dev/null
    rm /tmp/discovery_frontend.pid
fi

# Stop Docker services
cd docker
docker-compose down
cd ..

echo "All services stopped"
