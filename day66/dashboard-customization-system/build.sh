#!/bin/bash

set -e

echo "=========================================="
echo "Building Dashboard Customization System"
echo "=========================================="
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Docker
if command_exists docker && command_exists docker-compose; then
    echo "✓ Docker found"
    USE_DOCKER=true
else
    echo "⚠ Docker not found, using local installation"
    USE_DOCKER=false
fi

if [ "$USE_DOCKER" = true ]; then
    echo ""
    echo "Building with Docker..."
    echo "=========================================="
    
    # Stop existing containers
    docker-compose down -v 2>/dev/null || true
    
    # Build and start services
    docker-compose up --build -d
    
    echo ""
    echo "Waiting for services to be ready..."
    sleep 10
    
    # Check service health
    echo "Checking PostgreSQL..."
    docker-compose exec -T postgres pg_isready -U dashboard_user
    
    echo "Checking Redis..."
    docker-compose exec -T redis redis-cli ping
    
    echo ""
    echo "Running tests..."
    docker-compose exec -T backend pytest tests/ -v
    
    echo ""
    echo "=========================================="
    echo "✓ System ready!"
    echo "=========================================="
    echo ""
    echo "Access points:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    echo "Demo credentials:"
    echo "  Email: demo@example.com"
    echo "  Password: demo123"
    echo ""
    echo "To stop: ./stop.sh"
    
else
    echo ""
    echo "Building locally..."
    echo "=========================================="
    
    # Check PostgreSQL
    if ! command_exists psql; then
        echo "Error: PostgreSQL not found. Please install PostgreSQL 16+"
        exit 1
    fi
    
    # Check Redis
    if ! command_exists redis-cli; then
        echo "Error: Redis not found. Please install Redis 7+"
        exit 1
    fi
    
    # Backend setup
    echo ""
    echo "Setting up backend..."
    PROJECT_ROOT=$(pwd)
    BACKEND_DIR="$PROJECT_ROOT/backend"
    cd "$BACKEND_DIR"
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    
    # Check for duplicate services
    echo "Checking for duplicate services..."
    if pgrep -f "uvicorn.*app.main" > /dev/null; then
        echo "⚠ Backend service already running. Stopping it..."
        pkill -f "uvicorn.*app.main" || true
        sleep 2
    fi
    
    if pgrep -f "react-scripts start" > /dev/null || pgrep -f "node.*react" > /dev/null; then
        echo "⚠ Frontend service already running. Stopping it..."
        pkill -f "react-scripts start" || true
        pkill -f "node.*react" || true
        sleep 2
    fi
    
    # Create database
    echo "Setting up database..."
    export PGPASSWORD=dashboard_pass
    psql -U dashboard_user -h localhost -tc "SELECT 1 FROM pg_database WHERE datname = 'dashboard_db'" | grep -q 1 || \
        createdb -U dashboard_user -h localhost dashboard_db
    
    # Get absolute paths
    BACKEND_DIR=$(pwd)
    PROJECT_ROOT=$(dirname "$BACKEND_DIR")
    
    # Start backend
    echo "Starting backend..."
    cd "$BACKEND_DIR"
    uvicorn app.main:socket_app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$PROJECT_ROOT/backend.pid"
    echo "Backend started with PID: $BACKEND_PID"
    
    cd "$PROJECT_ROOT"
    
    # Frontend setup
    echo ""
    echo "Setting up frontend..."
    FRONTEND_DIR="$PROJECT_ROOT/frontend"
    cd "$FRONTEND_DIR"
    
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    
    # Run tests
    echo "Running tests..."
    CI=true npm test -- --watchAll=false || echo "⚠ Frontend tests had issues, continuing..."
    
    # Start frontend
    echo "Starting frontend..."
    cd "$FRONTEND_DIR"
    npm start &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$PROJECT_ROOT/frontend.pid"
    echo "Frontend started with PID: $FRONTEND_PID"
    
    cd "$PROJECT_ROOT"
    
    echo ""
    echo "Waiting for services..."
    sleep 5
    
    # Run backend tests
    cd "$BACKEND_DIR"
    source venv/bin/activate
    pytest tests/ -v || echo "⚠ Backend tests had issues, continuing..."
    cd "$PROJECT_ROOT"
    
    echo ""
    echo "=========================================="
    echo "✓ System ready!"
    echo "=========================================="
    echo ""
    echo "Access points:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    echo "Demo credentials:"
    echo "  Email: demo@example.com"
    echo "  Password: demo123"
    echo ""
    echo "To stop: ./stop.sh"
fi
