#!/bin/bash

echo "🛑 Stopping Day 98: Log Management Integration"

if command -v docker &> /dev/null; then
    if docker compose ps -q &> /dev/null || docker-compose ps -q &> /dev/null; then
        echo "🐳 Stopping Docker services..."
        docker compose down 2>/dev/null || docker-compose down
    fi
fi

if [ -f backend.pid ]; then
    echo "🛑 Stopping backend services..."
    while read pid; do
        kill $pid 2>/dev/null || true
    done < backend.pid
    rm backend.pid
fi

if [ -f frontend.pid ]; then
    echo "🛑 Stopping frontend..."
    kill $(cat frontend.pid) 2>/dev/null || true
    rm frontend.pid
fi

if pgrep redis-server > 0 2>/dev/null; then
    echo "🔴 Stopping Redis..."
    redis-cli shutdown 2>/dev/null || true
fi

echo "✅ All services stopped"
