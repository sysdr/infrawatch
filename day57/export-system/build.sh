#!/bin/bash

set -e

echo "🚀 Day 57: Export System Foundation - Build & Demo Script"
echo "=========================================================="

# Check if running with Docker
USE_DOCKER=${1:-"no-docker"}

if [ "$USE_DOCKER" == "docker" ]; then
    echo "🐳 Building and starting with Docker..."
    
    # Build and start all services
    docker-compose up -d --build
    
    echo "⏳ Waiting for services to be ready..."
    sleep 15
    
    echo "✅ Services started!"
    echo "📊 Backend API: http://localhost:8000"
    echo "🌐 Frontend Dashboard: http://localhost:3000"
    echo "📋 API Docs: http://localhost:8000/docs"
    echo ""
    echo "📝 View logs with: docker-compose logs -f"
    echo "🛑 Stop with: ./stop.sh docker"
    
else
    echo "💻 Building and starting without Docker..."
    
    # Install backend dependencies
    echo "📦 Installing backend dependencies..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Setup database
    echo "🗄️ Setting up database..."
    export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/exportdb"
    export REDIS_URL="redis://localhost:6379/0"
    
    # Check if PostgreSQL is running
    if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
        echo "⚠️  PostgreSQL is not running. Please start PostgreSQL first."
        echo "   On macOS: brew services start postgresql"
        echo "   On Ubuntu: sudo systemctl start postgresql"
        exit 1
    fi
    
    # Check if Redis is running
    if ! redis-cli ping > /dev/null 2>&1; then
        echo "⚠️  Redis is not running. Please start Redis first."
        echo "   On macOS: brew services start redis"
        echo "   On Ubuntu: sudo systemctl start redis"
        exit 1
    fi
    
    # Create database if not exists
    createdb exportdb 2>/dev/null || true
    
    # Seed data
    echo "🌱 Seeding test data..."
    python app/seed_data.py
    
    # Start Celery worker in background
    echo "🔄 Starting Celery worker..."
    celery -A app.celery_config.celery_app worker --loglevel=info > celery.log 2>&1 &
    CELERY_PID=$!
    echo $CELERY_PID > celery.pid
    
    # Start backend
    echo "🚀 Starting backend server..."
    uvicorn app.main:app --reload > backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > backend.pid
    
    cd ..
    
    # Install frontend dependencies
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    
    # Start frontend
    echo "🎨 Starting frontend..."
    npm start > frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > frontend.pid
    
    cd ..
    
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    echo "✅ All services started!"
    echo "📊 Backend API: http://localhost:8000"
    echo "🌐 Frontend Dashboard: http://localhost:3000"
    echo "📋 API Docs: http://localhost:8000/docs"
    echo ""
    echo "🛑 Stop with: ./stop.sh"
fi

echo ""
echo "🎯 Demo Instructions:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Select export format (CSV, JSON, PDF, or Excel)"
echo "3. Click 'Create Export' button"
echo "4. Watch the progress bar as export processes"
echo "5. Click 'Download Export' when completed"
echo "6. Verify downloaded file opens correctly"
echo ""
echo "🧪 Run tests:"
echo "   cd backend && source venv/bin/activate && pytest"
