#!/bin/bash

set -e

echo "🧪 Running tests for Day 29: Celery Task Queue System"

source venv/bin/activate
export PYTHONPATH=$PWD:$PYTHONPATH

# Run Python tests
echo "🐍 Running Python tests..."
pytest tests/ -v

echo "✅ All tests passed!"
