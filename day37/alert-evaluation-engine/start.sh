#!/bin/bash

echo "🚀 Starting Alert Evaluation Engine"
echo "================================="

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Check if ports are available
if port_in_use 8000; then
    echo "⚠️  Port 8000 is already in use (Backend)"
fi

if port_in_use 3000; then
    echo "⚠️  Port 3000 is already in use (Frontend)"
fi

# Start Redis and PostgreSQL with Docker if available
if command -v docker >/dev/null 2>&1; then
    echo "🐳 Starting infrastructure services..."
    docker run -d --name alert-redis -p 6379:6379 redis:7-alpine || echo "Redis container already running"
    docker run -d --name alert-postgres -p 5432:5432 -e POSTGRES_DB=alertdb -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password postgres:15-alpine || echo "PostgreSQL container already running"
    sleep 5
else
    echo "⚠️  Docker not available - make sure Redis and PostgreSQL are running locally"
fi

# Start Backend
echo "🐍 Starting Python backend..."
cd backend
source venv/bin/activate
python -m src.main &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 10

# Start Frontend
echo "⚛️  Starting React frontend..."
cd ../frontend
npm start &
FRONTEND_PID=$!

# Store PIDs for cleanup
echo $BACKEND_PID > ../backend.pid
echo $FRONTEND_PID > ../frontend.pid

echo ""
echo "🎉 Application started successfully!"
echo ""
echo "Services running:"
echo "  - Backend API: http://localhost:8000"
echo "  - API Documentation: http://localhost:8000/docs"
echo "  - Frontend: http://localhost:3000"
echo ""
echo "To stop the application, run: ./stop.sh"

# Keep script running
wait
