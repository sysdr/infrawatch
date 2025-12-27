#!/bin/bash

set -e

echo "=================================================="
echo "Building User Management System"
echo "=================================================="

MODE=${1:-no-docker}

if [ "$MODE" = "docker" ]; then
    echo "Building with Docker..."
    cd docker
    docker-compose up -d
    echo "✓ System started with Docker"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
else
    echo "Building without Docker..."
    
    # Backend
    echo "Setting up backend..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Start PostgreSQL and Redis (assumes they're installed)
    echo "Starting services..."
    if [ -f "../start-services.sh" ]; then
        bash ../start-services.sh
    else
        echo "⚠️  Please ensure PostgreSQL and Redis are running"
        echo "   Run: ./start-services.sh (if available)"
        echo "   OR start manually:"
        echo "   - PostgreSQL: sudo systemctl start postgresql"
        echo "   - Redis: sudo systemctl start redis"
    fi
    
    # Run migrations
    alembic init migrations || true
    
    echo "Starting backend server..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd ..
    
    # Frontend
    echo "Setting up frontend..."
    cd frontend
    npm install
    echo "Starting frontend..."
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo "✓ System started"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
    
    # Run tests
    echo ""
    echo "Running tests..."
    cd backend
    source venv/bin/activate
    pytest tests/ -v
    cd ..
    
    echo ""
    echo "System is running. Press Ctrl+C to stop."
    echo "PIDs - Backend: $BACKEND_PID, Frontend: $FRONTEND_PID"
    
    wait
fi
