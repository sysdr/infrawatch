#!/bin/bash

echo "Stopping services..."

# Stop backend
if [ -f backend/backend.pid ]; then
    kill $(cat backend/backend.pid) 2>/dev/null || true
    rm backend/backend.pid
fi

# Stop frontend
if [ -f frontend/frontend.pid ]; then
    kill $(cat frontend/frontend.pid) 2>/dev/null || true
    rm frontend/frontend.pid
fi

# Stop Docker containers
docker stop user-mgmt-postgres user-mgmt-redis 2>/dev/null || true

echo "✓ All services stopped"
