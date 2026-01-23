#!/bin/bash
# Complete frontend startup script

cd "$(dirname "$0")/frontend"

echo "=========================================="
echo "Starting Infrastructure Discovery Frontend"
echo "=========================================="

# Step 1: Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install --legacy-peer-deps
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

# Step 2: Fix permissions (for Windows mounts)
if [[ "$(pwd)" == /mnt/* ]]; then
    echo "Fixing permissions for Windows mount..."
    chmod -R u+w node_modules/.bin 2>/dev/null || true
fi

# Step 3: Start the frontend
echo "Starting frontend on port 3001..."
echo "This may take 30-60 seconds to compile..."
echo ""
PORT=3001 BROWSER=none npx --yes react-scripts@5.0.1 start
