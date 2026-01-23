#!/bin/bash

# Frontend startup script with proper error handling

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

cd "$FRONTEND_DIR"

echo "Starting frontend..."
echo "Directory: $FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "ERROR: node_modules not found. Installing dependencies..."
    npm install --legacy-peer-deps
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

# Check if react-scripts exists
if [ ! -f "node_modules/.bin/react-scripts" ] && [ ! -f "node_modules/react-scripts/bin/react-scripts.js" ]; then
    echo "WARNING: react-scripts not found. Reinstalling..."
    npm install react-scripts --legacy-peer-deps
fi

# Fix permissions if on Windows mount
if [[ "$FRONTEND_DIR" == /mnt/* ]]; then
    echo "Detected Windows mount, fixing permissions..."
    chmod -R u+w node_modules/.bin 2>/dev/null || true
fi

# Try to use npx first, fallback to node
PORT=${PORT:-3001}
echo "Starting on port $PORT..."

# Use npx which handles path resolution better
PORT=$PORT BROWSER=none npx --yes react-scripts start
