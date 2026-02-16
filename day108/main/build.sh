#!/bin/bash

echo "==================================="
echo "Building Custom Metrics Engine"
echo "==================================="

# Check if running with Docker
if [ "$1" == "--docker" ]; then
    echo "Building with Docker..."
    docker-compose up -d --build
    
    echo "Waiting for services to start..."
    sleep 10
    
    echo "Running tests..."
    docker-compose exec -T backend pytest tests/ -v
    
    echo "===================================  "
    echo "Services are running:"
    echo "Backend API: http://localhost:8000"
    echo "Frontend UI: http://localhost:3000"
    echo "==================================="
    
else
    echo "Building without Docker..."
    
    # Backend setup
    echo "Setting up backend..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Start PostgreSQL (assumes local installation)
    echo "Starting PostgreSQL..."
    export DATABASE_URL="postgresql://metrics_user:metrics_pass@localhost:5432/metrics_db"
    
    # Run database migrations
    python3 -c "from app.models.metric import Base; from sqlalchemy import create_engine; import os; engine = create_engine(os.getenv('DATABASE_URL')); Base.metadata.create_all(engine)"
    
    # Run tests
    echo "Running backend tests..."
    pytest tests/ -v
    
    # Start backend
    echo "Starting backend..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    cd ..
    
    # Frontend setup
    echo "Setting up frontend..."
    cd frontend
    npm install
    
    echo "Starting frontend..."
    HOST=0.0.0.0 BROWSER=none REACT_APP_API_URL=http://localhost:8000 npm start &
    FRONTEND_PID=$!
    
    cd ..
    
    echo "===================================  "
    echo "Services are running:"
    echo "Backend API: http://localhost:8000"
    echo "Frontend UI: http://localhost:3000"
    echo "Backend PID: $BACKEND_PID"
    echo "Frontend PID: $FRONTEND_PID"
    echo "==================================="
    
    # Save PIDs
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid
fi
