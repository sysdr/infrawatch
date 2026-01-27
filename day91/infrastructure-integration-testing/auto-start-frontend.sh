#!/bin/bash

# This script waits for npm install to complete, then starts the frontend

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

cd "$FRONTEND_DIR"

echo "Waiting for npm install to complete..."
while pgrep -f "npm install" > /dev/null; do
    sleep 5
done

echo "npm install completed!"
echo "Starting frontend server..."

# Fix permissions
if [ -d "node_modules/.bin" ]; then
    chmod +x node_modules/.bin/* 2>/dev/null || true
fi

# Stop any existing frontend
pkill -f "react-scripts start" 2>/dev/null || true
sleep 2

# Start frontend
BROWSER=none nohup npx react-scripts start > "$SCRIPT_DIR/frontend.log" 2>&1 &
echo $! > "$SCRIPT_DIR/frontend.pid"

echo "Frontend starting... (check http://localhost:3000 in 30-60 seconds)"
echo "Monitor with: tail -f $SCRIPT_DIR/frontend.log"
