#!/bin/bash

set -e

echo "======================================"
echo "Building Log Aggregation System"
echo "======================================"

# Check if running with Docker
if [ "$1" == "--docker" ]; then
    echo "Building with Docker..."
    cd docker
    docker-compose up -d
    
    echo "Waiting for services to be ready..."
    sleep 10
    
    echo "Services started:"
    docker-compose ps
    
    echo ""
    echo "Access the application:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: ./stop.sh --docker"
    
    exit 0
fi

# Non-Docker setup
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing backend dependencies..."
pip install -q -r backend/requirements.txt

echo "Installing frontend dependencies..."
cd frontend
npm install --silent
cd ..

echo "Starting PostgreSQL (ensure it's running)..."
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "Please start PostgreSQL on localhost:5432"
    echo "Or use: ./build.sh --docker"
    exit 1
fi

echo "Starting Redis (ensure it's running)..."
if ! redis-cli -h localhost -p 6379 ping > /dev/null 2>&1; then
    echo "Please start Redis on localhost:6379"
    echo "Or use: ./build.sh --docker"
    exit 1
fi

echo "Starting backend..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

sleep 5

echo "Starting log shipper..."
cd shipper
python shipper.py &
SHIPPER_PID=$!
cd ..

echo "Starting frontend..."
cd frontend
PORT=3000 npm start &
FRONTEND_PID=$!
cd ..

echo "$BACKEND_PID" > .backend.pid
echo "$SHIPPER_PID" > .shipper.pid
echo "$FRONTEND_PID" > .frontend.pid

echo ""
echo "======================================"
echo "System started successfully!"
echo "======================================"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Generating test logs..."
sleep 3
python tests/generate_logs.py data/logs 1000 json
python tests/generate_logs.py data/logs 500 apache
python tests/generate_logs.py data/logs 500 plain

echo ""
echo "Running tests..."
pytest tests/test_backend.py -v

echo ""
echo "To stop all services: ./stop.sh"
