#!/bin/bash

echo "=========================================="
echo "Building Real-time Performance System"
echo "=========================================="

# Check if Docker should be used
USE_DOCKER=${1:-"no"}

if [ "$USE_DOCKER" == "docker" ]; then
    echo "Building with Docker..."
    cd docker
    docker-compose up -d
    echo "Waiting for services to be ready..."
    sleep 10
    echo "Services started successfully!"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
else
    echo "Building without Docker..."
    
    # Start PostgreSQL and Redis (assumes they're installed)
    echo "Ensure PostgreSQL and Redis are running..."

    # Provide default local DATABASE_URL if not already set
    if [ -z "$DATABASE_URL" ]; then
        export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/notifications_db"
        echo "Using default DATABASE_URL for local Postgres instance."
    fi
    
    # Backend
    echo "Setting up backend..."
    cd backend
    # Try to create venv, fallback to --without-pip if ensurepip is missing
    if ! python3 -m venv venv 2>/dev/null; then
        echo "Creating venv without pip..."
        python3 -m venv --without-pip venv
        source venv/bin/activate
        # Install pip manually
        curl -sS https://bootstrap.pypa.io/get-pip.py | python3
    else
        source venv/bin/activate
        pip install --upgrade pip
    fi
    pip install -r requirements.txt
    
    # Create database (if psql is available)
    if command -v psql &> /dev/null; then
        export PGPASSWORD=postgres
        psql -h localhost -U postgres -c "CREATE DATABASE notifications_db;" || echo "Database creation skipped or failed"
    else
        echo "Warning: psql not found. Database creation skipped. Install postgresql-client if needed."
    fi
    
    # Start backend
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    cd ..
    
    # Frontend
    echo "Setting up frontend..."
    cd frontend
    npm install
    npm start &
    FRONTEND_PID=$!
    
    cd ..
    
    echo "Services started!"
    echo "Backend PID: $BACKEND_PID"
    echo "Frontend PID: $FRONTEND_PID"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    
    # Save PIDs
    echo $BACKEND_PID > backend.pid
    echo $FRONTEND_PID > frontend.pid
fi

echo "=========================================="
echo "Build Complete!"
echo "=========================================="
