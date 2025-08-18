#!/bin/bash

echo "🛑 Stopping Metrics Data Models System"

# Kill backend if running
if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null
    rm backend.pid
fi

# Kill frontend if running
if [ -f frontend.pid ]; then
    kill $(cat frontend.pid) 2>/dev/null
    rm frontend.pid
fi

# Stop Docker services
docker-compose down

echo "✅ System stopped"
