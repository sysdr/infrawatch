#!/bin/bash

echo "🛑 Stopping Day 46 services..."

# Kill backend
if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null
    rm backend.pid
    echo "✅ Backend stopped"
fi

# Kill frontend  
if [ -f frontend.pid ]; then
    kill $(cat frontend.pid) 2>/dev/null
    rm frontend.pid
    echo "✅ Frontend stopped"
fi

# Kill any remaining uvicorn processes
pkill -f uvicorn 2>/dev/null

echo "🎯 All services stopped"
