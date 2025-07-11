#!/bin/bash

# React Authentication UI - Start Script
# Kills any existing processes on port 3000 and starts development server

echo "🚀 Starting React Authentication UI..."
echo "============================================="

# Kill any existing processes on port 3000
echo "🔍 Checking for existing processes on port 3000..."
EXISTING_PID=$(lsof -ti:3000)

if [ ! -z "$EXISTING_PID" ]; then
    echo "⚠️  Found existing process on port 3000 (PID: $EXISTING_PID)"
    echo "🔪 Killing existing process..."
    kill -9 $EXISTING_PID
    sleep 1
    echo "✅ Process killed successfully"
else
    echo "✅ No existing processes found on port 3000"
fi

# Start the React development server
echo "🚀 Starting React development server..."
echo "📱 App will be available at: http://localhost:3000"
echo "⏹️  Press Ctrl+C to stop the server"
echo "============================================="

npm start 