#!/bin/bash

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Running tests..."
echo "Project root: $PROJECT_ROOT"

BACKEND_DIR="$PROJECT_ROOT/backend"
cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found. Please run $PROJECT_ROOT/scripts/build.sh first"
    exit 1
fi

source venv/bin/activate
pytest tests/ -v
cd "$PROJECT_ROOT"

echo "Tests complete!"
