#!/bin/bash

echo "🛑 Stopping Alert Management System..."

# Kill processes if PID files exist
if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null || true
    rm backend.pid
fi

if [ -f frontend.pid ]; then
    kill $(cat frontend.pid) 2>/dev/null || true
    rm frontend.pid
fi

# Kill any remaining processes
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "npm start" 2>/dev/null || true

echo "✅ System stopped successfully!"
