#!/bin/bash

echo "🛑 Stopping Notification System..."

# Kill backend
if [ -f .backend_pid ]; then
    BACKEND_PID=$(cat .backend_pid)
    kill $BACKEND_PID 2>/dev/null
    rm .backend_pid
    echo "🔧 Backend stopped"
fi

# Kill frontend  
if [ -f .frontend_pid ]; then
    FRONTEND_PID=$(cat .frontend_pid)
    kill $FRONTEND_PID 2>/dev/null
    rm .frontend_pid
    echo "🌐 Frontend stopped"
fi

# Kill any remaining processes
pkill -f "python app/main.py" 2>/dev/null
pkill -f "npm start" 2>/dev/null
pkill -f "react-scripts start" 2>/dev/null

echo "✅ All processes stopped"
