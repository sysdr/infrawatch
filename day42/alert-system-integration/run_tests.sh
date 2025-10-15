#!/bin/bash
set -e

echo "🧪 Running Alert System Tests..."

cd backend
source venv/bin/activate

echo "Running unit and integration tests..."
pytest -v

echo ""
echo "✅ All tests passed!"
