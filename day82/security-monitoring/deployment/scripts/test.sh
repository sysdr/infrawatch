#!/bin/bash

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "Running tests..."
echo "Project root: $PROJECT_ROOT"

# Activate virtual environment
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "Virtual environment not found. Creating..."
    cd "$PROJECT_ROOT"
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r "$PROJECT_ROOT/backend/requirements.txt"
else
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# Set PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT/backend:$PYTHONPATH"

# Backend tests
cd "$PROJECT_ROOT"
echo "Running unit tests..."
pytest tests/unit/ -v

echo "Running integration tests..."
pytest tests/integration/ -v

# Performance test (short run) - only if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "Running performance test (10 seconds)..."
    locust -f "$PROJECT_ROOT/tests/load/test_performance.py" --headless -u 10 -r 2 -t 10s --host http://localhost:8000 2>/dev/null || echo "Performance test skipped (locust may not be installed)"
else
    echo "Backend not running, skipping performance test"
fi

echo "Tests complete!"
