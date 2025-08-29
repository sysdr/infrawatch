#!/bin/bash

echo "🚀 Starting Day 26: Metrics API System"

# Activate virtual environment
source venv/bin/activate

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Start PostgreSQL and Redis (local installation)
echo "🐘 Starting PostgreSQL..."
if command -v brew &> /dev/null; then
    brew services start postgresql
    brew services start redis
elif command -v systemctl &> /dev/null; then
    sudo systemctl start postgresql
    sudo systemctl start redis
else
    echo "Please start PostgreSQL and Redis manually"
fi

# Wait for services
sleep 5

# Create database
echo "📊 Setting up database..."
createdb metrics_db || echo "Database already exists"

# Set environment variables
export DATABASE_URL="postgresql://$(whoami)@localhost/metrics_db"
export REDIS_URL="redis://localhost:6379/0"

# Start backend
echo "🐍 Starting backend API..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 10

# Start frontend
echo "⚛️ Starting frontend dashboard..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ System started successfully!"
echo "📊 API: http://localhost:8000"
echo "🌐 Dashboard: http://localhost:3000"
echo "📖 API Docs: http://localhost:8000/docs"

# Save PIDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

echo "Press Ctrl+C to stop all services"
wait
