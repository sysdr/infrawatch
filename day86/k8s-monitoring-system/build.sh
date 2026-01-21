#!/bin/bash

echo "========================================="
echo "Building K8s Monitoring System"
echo "========================================="

# Setup backend
echo "Setting up Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt asyncpg

echo "Running tests..."
cd ..
pytest tests/ -v

echo "========================================="
echo "Build complete!"
echo ""
echo "To run without Docker:"
echo "  1. Start PostgreSQL: docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=k8s_password -e POSTGRES_USER=k8s_user -e POSTGRES_DB=k8s_monitor postgres:16-alpine"
echo "  2. Start Redis: docker run -d -p 6379:6379 redis:7-alpine"
echo "  3. Start backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "  4. Start frontend: cd frontend && npm install && npm start"
echo ""
echo "To run with Docker:"
echo "  docker-compose up --build"
echo "========================================="
