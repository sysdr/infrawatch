#!/bin/bash
# Wrapper script to start React dev server

cd "$(dirname "$0")"

# Set port and bind to all interfaces (WSL2: accessible from Windows localhost)
export PORT=${PORT:-3001}
export HOST=0.0.0.0
export BROWSER=none
export DANGEROUSLY_DISABLE_HOST_CHECK=true

# Check if dependencies are installed
if [ ! -d "node_modules" ] || [ ! -d "node_modules/react-scripts" ]; then
    echo "Installing dependencies..."
    npm install --legacy-peer-deps
fi

# Check if webpack exists (required by react-scripts)
if [ ! -d "node_modules/webpack" ]; then
    echo "Installing missing dependencies..."
    npm install --legacy-peer-deps
fi

# Use node directly to run react-scripts
echo "Starting frontend on port $PORT..."
node node_modules/react-scripts/scripts/start.js
