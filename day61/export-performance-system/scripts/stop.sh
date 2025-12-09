#!/bin/bash

echo "Stopping Export Performance System..."

if [ -f /tmp/backend.pid ]; then
    kill $(cat /tmp/backend.pid) 2>/dev/null || true
    rm /tmp/backend.pid
fi

if [ -f /tmp/frontend.pid ]; then
    kill $(cat /tmp/frontend.pid) 2>/dev/null || true
    rm /tmp/frontend.pid
fi

# Stop Docker if running
docker-compose down 2>/dev/null || true

echo "Services stopped"
