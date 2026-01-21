#!/bin/bash

# Frontend startup script

cd "$(dirname "$0")"

echo "============================================"
echo "Starting Container Monitoring Frontend"
echo "============================================"
echo ""

# Check if we're in the right directory
if [ ! -d "frontend" ]; then
    echo "Error: Please run this script from the container-monitoring directory"
    exit 1
fi

cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo ""
echo "Starting frontend development server..."
echo "Dashboard will be available at: http://localhost:3000"
echo "(Check terminal for actual port if 3000 is in use)"
echo ""
echo "Press Ctrl+C to stop"
echo ""

npm run dev
