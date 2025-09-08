#!/bin/bash

echo "🛑 Stopping Day 30: Async Task Implementation"
echo "============================================="

# Kill processes if PID files exist
if [ -f celery_worker.pid ]; then
    kill $(cat celery_worker.pid) 2>/dev/null || echo "Celery worker already stopped"
    rm celery_worker.pid
fi

if [ -f celery_beat.pid ]; then
    kill $(cat celery_beat.pid) 2>/dev/null || echo "Celery beat already stopped"
    rm celery_beat.pid
fi

if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null || echo "Backend already stopped"
    rm backend.pid
fi

if [ -f frontend.pid ]; then
    kill $(cat frontend.pid) 2>/dev/null || echo "Frontend already stopped"
    rm frontend.pid
fi

# Kill any remaining processes
pkill -f "celery.*config.celery_config" 2>/dev/null || true
pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
pkill -f "npm start" 2>/dev/null || true

echo "✅ All services stopped"
