#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "Running Tests"
echo "=========================================="

cd "$PROJECT_ROOT/backend"
source venv/bin/activate
export PYTHONPATH="$PROJECT_ROOT/backend:$PROJECT_ROOT:$PYTHONPATH"

# Run pytest
pytest "$PROJECT_ROOT/tests/" -v --tb=short

echo ""
echo "All tests passed!"
