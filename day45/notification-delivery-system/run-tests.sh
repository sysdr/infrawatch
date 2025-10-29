#!/bin/bash

echo "🧪 Running comprehensive tests..."

# Activate virtual environment
source venv/bin/activate

# Run backend tests
echo "🔧 Running backend tests..."
cd backend
python -m pytest tests/ -v --tb=short
cd ..

# Run frontend tests (if any)
echo "🎨 Running frontend tests..."
cd frontend
npm test -- --coverage --watchAll=false
cd ..

echo "✅ All tests completed!"
