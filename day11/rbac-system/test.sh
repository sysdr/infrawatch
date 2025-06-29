#!/bin/bash

set -e

echo "🧪 Running RBAC System Tests..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install test dependencies
pip install pytest pytest-asyncio httpx

# Set test database URL
export DATABASE_URL=postgresql://postgres:password@localhost:5432/rbac_test

# Ensure test database exists
python scripts/setup_test_db.py

# Run tests
echo "🔬 Running unit tests..."
python -m pytest tests/ -v

echo "🔍 Running integration tests..."
python -m pytest tests/test_rbac.py::test_admin_access_control -v

echo "✅ All tests completed!"
