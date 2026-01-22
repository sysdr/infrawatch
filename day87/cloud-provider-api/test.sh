#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Running tests..."

BACKEND_DIR="$SCRIPT_DIR/backend"
TESTS_DIR="$SCRIPT_DIR/tests"

if [ ! -d "$BACKEND_DIR" ]; then
    echo "ERROR: Backend directory not found at $BACKEND_DIR"
    exit 1
fi

if [ ! -d "$TESTS_DIR" ]; then
    echo "ERROR: Tests directory not found at $TESTS_DIR"
    exit 1
fi

cd "$BACKEND_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found. Run build.sh first."
    exit 1
fi

# Activate venv
source venv/bin/activate

# Run tests
echo "Running pytest from $BACKEND_DIR on $TESTS_DIR..."
cd "$BACKEND_DIR"
PYTHONPATH="$BACKEND_DIR:$PYTHONPATH" python -m pytest "$TESTS_DIR" -v

echo "✓ Tests completed"
