#!/bin/bash

echo "========================================="
echo "Building Log Retention & Archival System"
echo "========================================="

# Check if running with Docker
if [ "$1" == "--docker" ]; then
    echo "Building with Docker..."
    docker-compose up -d
    
    echo "Waiting for services to start..."
    sleep 10
    
    echo "System ready!"
    echo "Frontend: http://localhost:3000"
    echo "Backend: http://localhost:8000"
    echo "MinIO Console: http://localhost:9001"
    exit 0
fi

# Without Docker
echo "Building without Docker..."

# Backend
echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start PostgreSQL if not running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "Please start PostgreSQL on port 5432"
    exit 1
fi

# Start Redis if not running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "Please start Redis on port 6379"
    exit 1
fi

# Initialize database
python -c "from models.database import init_db; init_db()"

# Start backend
echo "Starting backend..."
python api/main.py &
BACKEND_PID=$!

cd ..

# Frontend
echo "Setting up frontend..."
cd frontend
npm install
npm run build

echo "Starting frontend..."
npm start &
FRONTEND_PID=$!

cd ..

# Run tests (from backend so .env is loaded)
echo "Running tests..."
cd "$(dirname "$0")"
cd backend && PYTHONPATH=. pytest ../tests/test_retention.py -v
cd ..

echo ""
echo "========================================="
echo "System is running!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "========================================="
echo ""
echo "Press Ctrl+C to stop"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
