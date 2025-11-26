#!/bin/bash

echo "🧪 Running tests..."

# Backend tests
echo "Running backend integration tests..."
cd tests/integration
python3 -m pytest test_integration.py -v

cd ../..

# Load test
echo "Running load test..."
cd tests/load
python3 load_test.py

echo "✅ Tests complete!"
