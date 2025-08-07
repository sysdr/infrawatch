#!/bin/bash

echo "🧪 Running Tests"
echo "==============="

# Backend tests
echo "Testing backend..."
cd backend
source venv/bin/activate
python -m pytest tests/ -v

# Frontend tests
echo "Testing frontend..."
cd ../frontend
npm test -- --coverage --watchAll=false

echo "✅ All tests completed"
