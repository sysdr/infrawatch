#!/bin/bash

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="${SCRIPT_DIR}/frontend"

# Check if frontend directory exists
if [ ! -d "${FRONTEND_DIR}" ]; then
    echo "Error: Frontend directory not found at ${FRONTEND_DIR}"
    exit 1
fi

# Change to frontend directory
cd "${FRONTEND_DIR}" || exit 1

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Error: node_modules not found. Please run ./build.sh first"
    exit 1
fi

# Start frontend server
npm run dev
