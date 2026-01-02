#!/bin/bash

# Get absolute path of script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "🧪 Running tests in Docker container..."

# Ensure test database exists (ignore error if it already exists)
docker-compose exec -T postgres psql -U rbac_user -d postgres -c "CREATE DATABASE rbac_test_db;" > /dev/null 2>&1 || true

# Run tests in backend container
docker-compose exec -T backend sh -c "cd /app && TEST_DATABASE_URL='postgresql://rbac_user:rbac_pass@postgres:5432/rbac_test_db' PYTHONPATH=/app pytest tests/test_rbac.py -v"

echo "✅ Tests completed"
