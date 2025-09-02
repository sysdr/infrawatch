#!/bin/bash

echo "🛑 Stopping Metrics Dashboard"
echo "============================="

# Kill backend if PID file exists
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        echo "🖥️ Stopping backend server..."
        kill $BACKEND_PID
    fi
    rm backend.pid
fi

# Kill frontend if PID file exists  
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "🌐 Stopping frontend server..."
        kill $FRONTEND_PID
    fi
    rm frontend.pid
fi

# Kill any remaining processes
pkill -f "python -m app.main"
pkill -f "npm start"

echo "✅ Dashboard stopped successfully!"
