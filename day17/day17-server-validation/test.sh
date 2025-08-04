#!/bin/bash

echo "🧪 Running Day 17 Tests"

# Test backend
echo "Testing backend..."
cd backend
python -m pytest tests/ -v
cd ..

# Test frontend
echo "Testing frontend..."
cd frontend
npm test -- --coverage --watchAll=false
cd ..

echo "✅ All tests completed"
