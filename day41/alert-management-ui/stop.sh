#!/bin/bash

echo "🛑 Stopping Alert Management UI System"

# Kill backend
if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null
    rm backend.pid
fi

# Kill frontend  
if [ -f frontend.pid ]; then
    kill $(cat frontend.pid) 2>/dev/null
    rm frontend.pid
fi

# Kill any remaining processes
pkill -f "uvicorn.*main:app"
pkill -f "react-scripts.*start"

echo "✅ All services stopped"
