#!/bin/bash

echo "🧪 Running tests..."

# Backend tests
cd backend
source venv/bin/activate
echo "Running backend tests..."
pytest tests/ -v

# Frontend tests
cd ../frontend
echo "Running frontend tests..."
npm test -- --coverage --watchAll=false

echo "✅ All tests completed!"
