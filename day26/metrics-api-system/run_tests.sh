#!/bin/bash

echo "🧪 Running Day 26: Metrics API Tests"

# Activate virtual environment
source venv/bin/activate

# Set test environment
export DATABASE_URL="postgresql://sds:password@localhost/metrics_test_db"
export REDIS_URL="redis://localhost:6379/1"

# Create test database
createdb metrics_test_db || echo "Test database already exists"

# Initialize test database
echo "Initializing test database..."
cd backend
python -c "
import asyncio
from config.database import init_db
asyncio.run(init_db())
print('Database initialized successfully')
"
cd ..

# Run backend tests
echo "Testing backend..."
cd backend
python -m pytest tests/ -v --cov=app --cov-report=html
cd ..

echo "✅ Tests completed"
