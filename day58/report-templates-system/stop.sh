#!/bin/bash

echo "Stopping Report Templates System..."

# Kill backend processes
if [ -f .api.pid ]; then
    kill $(cat .api.pid) 2>/dev/null
    rm .api.pid
fi

if [ -f .scheduler.pid ]; then
    kill $(cat .scheduler.pid) 2>/dev/null
    rm .scheduler.pid
fi

if [ -f .frontend.pid ]; then
    kill $(cat .frontend.pid) 2>/dev/null
    rm .frontend.pid
fi

# Stop Docker containers
docker stop reports-postgres reports-redis 2>/dev/null
docker rm reports-postgres reports-redis 2>/dev/null

# Stop docker-compose if used
cd docker 2>/dev/null && docker-compose down 2>/dev/null

echo "All services stopped"
