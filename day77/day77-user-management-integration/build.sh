#!/bin/bash

set -e

echo "========================================"
echo "Building User Management Integration System"
echo "========================================"

# Start services
echo "Checking PostgreSQL and Redis..."
USE_DOCKER=false

# Check if PostgreSQL is already running
if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    echo "✓ PostgreSQL is already running on port 5432"
    USE_DOCKER=false
elif command -v docker &> /dev/null; then
    echo "Starting PostgreSQL with Docker..."
    docker run -d --name user-mgmt-postgres \
        -e POSTGRES_PASSWORD=postgres \
        -e POSTGRES_DB=user_management \
        -p 5432:5432 \
        postgres:16-alpine 2>/dev/null || docker start user-mgmt-postgres 2>/dev/null || echo "Warning: Could not start PostgreSQL container"
    USE_DOCKER=true
else
    echo "Warning: PostgreSQL not found and Docker not available"
fi

# Check if Redis is already running
if redis-cli -h localhost -p 6379 ping >/dev/null 2>&1; then
    echo "✓ Redis is already running on port 6379"
elif command -v docker &> /dev/null; then
    echo "Starting Redis with Docker..."
    docker run -d --name user-mgmt-redis \
        -p 6379:6379 \
        redis:7-alpine 2>/dev/null || docker start user-mgmt-redis 2>/dev/null || echo "Warning: Could not start Redis container"
else
    echo "Warning: Redis not found and Docker not available"
fi

echo "Waiting for services to be ready..."
sleep 5

# Setup Backend
echo "Setting up backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run backend
echo "Starting backend server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid

cd ..

# Setup Frontend
echo "Setting up frontend..."
cd frontend

# Install dependencies
npm install

# Start frontend
echo "Starting frontend..."
npm start &
FRONTEND_PID=$!
echo $FRONTEND_PID > frontend.pid

cd ..

echo "========================================"
echo "✓ Build Complete!"
echo "========================================"
echo "Backend running on: http://localhost:8000"
echo "Frontend running on: http://localhost:3000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "To stop services, run: ./stop.sh"
echo "========================================"

# Services are running in background
echo ""
echo "Services started. Check logs if needed."
echo "Backend PID: $(cat backend/backend.pid 2>/dev/null || echo 'N/A')"
echo "Frontend PID: $(cat frontend/frontend.pid 2>/dev/null || echo 'N/A')"
