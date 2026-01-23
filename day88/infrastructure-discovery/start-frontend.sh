#!/bin/bash
# Simple frontend starter - waits for dependencies then starts

cd "$(dirname "$0")/frontend" || exit 1

echo "=========================================="
echo "Infrastructure Discovery Frontend Starter"
echo "=========================================="

# Check dependencies
if [ ! -d "node_modules/webpack" ] || [ ! -d "node_modules/react-scripts" ]; then
    echo "⚠️  Dependencies not ready yet."
    echo "Waiting for npm install to complete..."
    
    # Wait up to 5 minutes for dependencies
    for i in {1..60}; do
        sleep 5
        if [ -d "node_modules/webpack" ] && [ -d "node_modules/react-scripts" ]; then
            echo "✅ Dependencies ready!"
            break
        fi
        echo -n "."
    done
    
    if [ ! -d "node_modules/webpack" ]; then
        echo ""
        echo "❌ Dependencies still not ready. Please run:"
        echo "   cd frontend && npm install --legacy-peer-deps"
        exit 1
    fi
fi

# Set port
export PORT=${PORT:-3001}
export BROWSER=none

echo "Starting frontend on port $PORT..."
echo "This will take 30-60 seconds to compile..."
echo ""
echo "Once you see 'Compiled successfully!',"
echo "open http://localhost:$PORT in your browser"
echo ""

# Start the frontend
node node_modules/react-scripts/scripts/start.js
