#!/bin/bash

echo "🛑 Stopping Day 24: Metrics Storage & Retrieval System"

# Kill backend process
if [ -f backend.pid ]; then
    BACKEND_PID=$(cat backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
    fi
    rm backend.pid
fi

# Kill frontend process  
if [ -f frontend.pid ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
    fi
    rm frontend.pid
fi

echo "✅ All services stopped!"
