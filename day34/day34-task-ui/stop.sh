#!/bin/bash

echo "🛑 Stopping Task Management UI Dashboard"
echo "======================================="

# Stop backend
if [ -f backend.pid ]; then
    BACKEND_PID=$(cat backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        echo "✅ Backend stopped (PID: $BACKEND_PID)"
    fi
    rm -f backend.pid
fi

# Stop frontend
if [ -f frontend.pid ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        echo "✅ Frontend stopped (PID: $FRONTEND_PID)"
    fi
    rm -f frontend.pid
fi

# Stop Redis if we started it
if pgrep -x "redis-server" > /dev/null; then
    echo "⚠️  Redis is still running (may be used by other processes)"
fi

echo "🎉 All services stopped"
