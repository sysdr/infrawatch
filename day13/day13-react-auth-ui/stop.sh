#!/bin/bash

# React Authentication UI - Stop Script
# Kills the React development server and related processes

echo "🛑 Stopping React Authentication UI..."
echo "============================================="

# Kill processes on port 3000 (React dev server)
echo "🔍 Checking for processes on port 3000..."
REACT_PID=$(lsof -ti:3000)

if [ ! -z "$REACT_PID" ]; then
    echo "⚠️  Found React dev server (PID: $REACT_PID)"
    echo "🔪 Killing React development server..."
    kill -9 $REACT_PID
    sleep 1
    echo "✅ React development server stopped"
else
    echo "✅ No React development server found"
fi

# Kill any remaining node processes related to react-scripts
echo "🔍 Checking for react-scripts processes..."
REACT_SCRIPTS_PIDS=$(pgrep -f "react-scripts")

if [ ! -z "$REACT_SCRIPTS_PIDS" ]; then
    echo "⚠️  Found react-scripts processes: $REACT_SCRIPTS_PIDS"
    echo "🔪 Killing react-scripts processes..."
    echo $REACT_SCRIPTS_PIDS | xargs kill -9 2>/dev/null
    sleep 1
    echo "✅ react-scripts processes stopped"
else
    echo "✅ No react-scripts processes found"
fi

# Check for any remaining Node.js processes on common development ports
echo "🔍 Checking for other development processes..."
OTHER_PIDS=$(lsof -ti:3001,3002,3003,8000,8080 2>/dev/null)

if [ ! -z "$OTHER_PIDS" ]; then
    echo "⚠️  Found other development processes on ports 3001-3003, 8000, 8080"
    echo "🔪 Killing other development processes..."
    echo $OTHER_PIDS | xargs kill -9 2>/dev/null
    sleep 1
    echo "✅ Other development processes stopped"
else
    echo "✅ No other development processes found"
fi

echo "============================================="
echo "🏁 All development servers stopped successfully!"
echo "✨ Ready to start fresh with ./start.sh" 