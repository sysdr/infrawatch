#!/bin/bash

set -e

echo "🚀 Starting Metrics Aggregation System"

# Check if Docker is available
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "📦 Docker detected - starting with Docker Compose"
    
    # Build and start services
    docker-compose down --remove-orphans
    docker-compose build
    docker-compose up -d
    
    # Wait for services to be healthy
    echo "⏳ Waiting for services to start..."
    sleep 30
    
    # Check health
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo "✅ Backend is healthy"
    else
        echo "❌ Backend health check failed"
        docker-compose logs backend
    fi
    
    if curl -f http://localhost:3000 &> /dev/null; then
        echo "✅ Frontend is healthy"
    else
        echo "❌ Frontend health check failed"
        docker-compose logs frontend
    fi
    
    echo "🎉 System started successfully!"
    echo "📊 Dashboard: http://localhost:3000"
    echo "🔧 API: http://localhost:8000"
    echo "📝 API Docs: http://localhost:8000/docs"
    
else
    echo "🐍 Docker not available - starting in development mode"
    
    # Backend setup
    echo "Setting up Python backend..."
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Start backend in background
    echo "Starting backend server..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    
    cd ..
    
    # Frontend setup
    echo "Setting up React frontend..."
    cd frontend
    
    # Install dependencies
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    
    # Start frontend in background
    echo "Starting frontend server..."
    npm start &
    FRONTEND_PID=$!
    
    cd ..
    
    # Save PIDs for cleanup
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid
    
    echo "⏳ Waiting for services to start..."
    sleep 15
    
    # Check services
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo "✅ Backend is running"
    else
        echo "❌ Backend failed to start"
    fi
    
    if curl -f http://localhost:3000 &> /dev/null; then
        echo "✅ Frontend is running"
    else
        echo "❌ Frontend failed to start"
    fi
    
    echo "🎉 Development environment started!"
    echo "📊 Dashboard: http://localhost:3000"
    echo "🔧 API: http://localhost:8000"
    echo "📝 API Docs: http://localhost:8000/docs"
fi

# Run tests
echo "🧪 Running tests..."
cd backend
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi
python -m pytest tests/ -v
cd ..

echo "✅ All tests passed!"
echo ""
echo "🚀 Metrics Aggregation System is ready!"
echo "📊 Open http://localhost:3000 to view the dashboard"
echo ""
echo "To stop the system, run: ./stop.sh"
