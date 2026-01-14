#!/bin/bash

echo "Building and starting Advanced Authentication System..."

# With Docker
echo "===== Building with Docker ====="
docker-compose up --build -d

echo "Waiting for services to be ready..."
sleep 15

echo "Services are running:"
echo "- Backend API: http://localhost:8000"
echo "- Frontend UI: http://localhost:3000"
echo "- API Docs: http://localhost:8000/docs"

echo ""
echo "===== Running Tests ====="
docker-compose exec backend sh -c "cd /app && PYTHONPATH=/app pytest tests/ -v" || echo "Tests failed"

echo ""
echo "===== System is ready! ====="
echo "Visit http://localhost:3000 to see the dashboard"
