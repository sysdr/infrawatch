#!/bin/bash

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Building Infrastructure Discovery System..."
echo "Project root: $PROJECT_ROOT"

# Backend setup
echo "Setting up backend..."
BACKEND_DIR="$PROJECT_ROOT/backend"
cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --quiet -r requirements.txt
cd "$PROJECT_ROOT"

# Frontend setup
echo "Setting up frontend..."
FRONTEND_DIR="$PROJECT_ROOT/frontend"
cd "$FRONTEND_DIR"
npm install --silent
cd "$PROJECT_ROOT"

echo "Build complete!"
echo "Run '$PROJECT_ROOT/scripts/start.sh' to start the system"
