#!/bin/bash

echo "=== Running Tests ==="

# Activate virtual environment
source venv/bin/activate

# Set Python path
export PYTHONPATH="${PWD}/backend/src:$PYTHONPATH"

# Run backend tests
echo "Running backend tests..."
cd backend
python -m pytest tests/ -v
cd ..

# Run frontend tests  
echo "Running frontend tests..."
cd frontend
npm test -- --coverage --watchAll=false
cd ..

echo "=== Tests Complete ==="
