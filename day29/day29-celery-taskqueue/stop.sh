#!/bin/bash

echo "🛑 Stopping Day 29: Celery Task Queue System"

# Kill processes by port
echo "Stopping services..."
pkill -f "python app/run.py" 2>/dev/null || true
pkill -f "python worker/start_worker.py" 2>/dev/null || true
pkill -f "npm start" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true

# Stop Docker containers
docker stop day29-redis 2>/dev/null || true
docker-compose down 2>/dev/null || true

echo "✅ All services stopped"
