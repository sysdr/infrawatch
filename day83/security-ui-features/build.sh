#!/bin/bash

set -e

echo "=========================================="
echo "Security UI Features - Build & Run"
echo "=========================================="
echo ""

# Check if running with Docker
if [ "$1" == "--docker" ]; then
    echo "Building and running with Docker..."
    cd docker
    docker-compose up --build -d
    
    echo ""
    echo "Waiting for services to be ready..."
    sleep 10
    
    echo ""
    echo "=========================================="
    echo "Services are running!"
    echo "=========================================="
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
    echo "To view logs: docker-compose -f docker/docker-compose.yml logs -f"
    echo "To stop: ./stop.sh --docker"
    echo "=========================================="
else
    echo "Building and running locally..."
    
    # Check for PostgreSQL
    echo "Checking PostgreSQL..."
    if ! command -v psql &> /dev/null; then
        echo "PostgreSQL not found. Please install PostgreSQL 16 or use Docker mode with --docker flag"
        exit 1
    fi
    
    # Check for Redis
    echo "Checking Redis..."
    if ! command -v redis-cli &> /dev/null; then
        echo "Redis not found. Please install Redis 7 or use Docker mode with --docker flag"
        exit 1
    fi
    
    # Setup database
    echo "Setting up database..."
    # Use environment variables or defaults for local development
    DB_USER="${DB_USER:-securityuser}"
    DB_PASSWORD="${DB_PASSWORD:-$(openssl rand -hex 16)}"
    DB_NAME="${DB_NAME:-securitydb}"
    DB_HOST="${DB_HOST:-localhost}"
    DB_PORT="${DB_PORT:-5432}"
    
    export DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
    export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
    
    # Create database if it doesn't exist
    psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}'" | grep -q 1 || \
        psql -U postgres -c "CREATE DATABASE ${DB_NAME};" 2>/dev/null || true
    
    psql -U postgres -tc "SELECT 1 FROM pg_roles WHERE rolname = '${DB_USER}'" | grep -q 1 || \
        psql -U postgres -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';" 2>/dev/null || true
    
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};" 2>/dev/null || true
    
    # Backend setup
    echo ""
    echo "Setting up backend..."
    cd backend
    
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
    
    echo "Starting backend server..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    
    cd ..
    
    # Frontend setup
    echo ""
    echo "Setting up frontend..."
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        echo "Installing dependencies..."
        npm install --silent
    fi
    
    echo "Starting frontend..."
    REACT_APP_API_URL=http://localhost:8000 \
    REACT_APP_WS_URL=ws://localhost:8000/ws/security/events \
    PORT=3000 npm start &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    
    cd ..
    
    echo ""
    echo "Waiting for services to start..."
    sleep 15
    
    # Run tests
    echo ""
    echo "Running backend tests..."
    cd backend
    source venv/bin/activate
    pytest tests/ -v --tb=short || true
    cd ..
    
    echo ""
    echo "=========================================="
    echo "Services are running!"
    echo "=========================================="
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
    echo "Backend PID: $BACKEND_PID"
    echo "Frontend PID: $FRONTEND_PID"
    echo ""
    echo "To stop: ./stop.sh"
    echo "=========================================="
    
    # Keep script running
    wait
fi
