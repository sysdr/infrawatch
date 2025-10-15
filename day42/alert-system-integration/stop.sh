#!/bin/bash

echo "🛑 Stopping Alert System Integration..."

if [ -f .backend.pid ]; then
    kill $(cat .backend.pid) 2>/dev/null
    rm .backend.pid
    echo "✅ Backend stopped"
fi

if [ -f .frontend.pid ]; then
    kill $(cat .frontend.pid) 2>/dev/null
    rm .frontend.pid
    echo "✅ Frontend stopped"
fi

# Kill any remaining processes
pkill -f "python run.py"
pkill -f "react-scripts start"

echo "✅ All services stopped"
