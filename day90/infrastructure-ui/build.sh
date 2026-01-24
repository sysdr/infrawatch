#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo "======================================"
echo "Infrastructure UI - Build Script"
echo "======================================"
echo "Working directory: $SCRIPT_DIR"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."
if ! command_exists python3; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

if ! command_exists node; then
    echo "Error: Node.js is not installed"
    exit 1
fi

if ! command_exists docker; then
    echo "Warning: Docker is not installed. Will run without Docker."
    DOCKER_AVAILABLE=false
else
    DOCKER_AVAILABLE=true
fi

echo "✓ Prerequisites checked"

# Ask user for deployment mode
echo ""
echo "Select deployment mode:"
echo "1) Without Docker (local development)"
echo "2) With Docker"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "2" ] && [ "$DOCKER_AVAILABLE" = true ]; then
    echo ""
    echo "======================================"
    echo "Building with Docker"
    echo "======================================"
    
    docker-compose down -v 2>/dev/null
    docker-compose up --build -d
    
    echo ""
    echo "Waiting for services to be ready..."
    sleep 10
    
    echo ""
    echo "✓ Services started successfully!"
    echo ""
    echo "Access the application:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
    
else
    echo ""
    echo "======================================"
    echo "Building without Docker"
    echo "======================================"
    
    # Backend setup
    echo ""
    echo "Setting up backend..."
    cd backend
    
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
    
    # Start PostgreSQL and Redis (assuming they're installed)
    echo "Note: Make sure PostgreSQL and Redis are running"
    echo "PostgreSQL should be on localhost:5432"
    echo "Redis should be on localhost:6379"
    
    # Start backend
    echo "Starting backend server..."
    export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5433/infradb"
    export REDIS_URL="redis://localhost:6379"
    
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    
    cd ..
    
    # Frontend setup
    echo ""
    echo "Setting up frontend..."
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        echo "Installing npm dependencies..."
        npm install
    fi
    
    echo "Starting frontend development server..."
    npm run dev &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    
    cd ..
    
    # Save PIDs for stop script
    echo "$BACKEND_PID" > .backend.pid
    echo "$FRONTEND_PID" > .frontend.pid
    
    echo ""
    echo "✓ Services started successfully!"
    echo ""
    echo "Access the application:"
    echo "  Frontend: http://localhost:5173"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    echo "To stop services, run: ./stop.sh"
    
    # Wait for user input
    echo ""
    echo "Press Ctrl+C to stop services..."
    wait
fi
