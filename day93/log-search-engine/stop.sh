#!/bin/bash

if [ -f "backend.pid" ]; then
    kill $(cat backend.pid) 2>/dev/null || true
    rm backend.pid
fi

if [ -f "frontend.pid" ]; then
    kill $(cat frontend.pid) 2>/dev/null || true
    rm frontend.pid
fi

docker-compose down 2>/dev/null || true

echo "Services stopped."
