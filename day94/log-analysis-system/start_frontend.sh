#!/bin/bash
# Start frontend with full path - run from anywhere
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

echo "Starting frontend - Dashboard: http://localhost:3001"
export PORT=3001
export HOST=0.0.0.0
exec npm start
