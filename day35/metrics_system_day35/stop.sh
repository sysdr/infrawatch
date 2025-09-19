#!/bin/bash

echo "🛑 Stopping Day 35: Background Processing Integration"
echo "=================================================="

if [ -f pids.txt ]; then
    echo "📋 Reading process IDs..."
    while IFS= read -r pid; do
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            echo "🔴 Stopping process $pid"
            kill "$pid"
        fi
    done < pids.txt
    rm pids.txt
    echo "✅ All processes stopped"
else
    echo "📋 No PID file found, attempting to find and stop processes..."
    
    # Try to find and stop processes by port
    pkill -f "uvicorn.*8000" || true
    pkill -f "celery.*worker" || true
    pkill -f "npm start" || true
    
    echo "✅ Cleanup completed"
fi

echo ""
echo "🧹 Cleaning up virtual environment..."
if [ -d "backend/venv" ]; then
    deactivate 2>/dev/null || true
    echo "✅ Virtual environment deactivated"
fi

echo ""
echo "✅ SHUTDOWN COMPLETE"
echo "All services have been stopped."
