#!/bin/bash

set -e

echo "🚀 Building Alert Management System..."

# Setup Python virtual environment
echo "📦 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Setup environment
echo "🔧 Setting up environment..."
export DATABASE_URL="sqlite:///./alert_system.db"

# Run tests
echo "🧪 Running tests..."
cd backend
python -m pytest tests/ -v
cd ..

echo "✅ Build completed successfully!"

# Start services
echo "🚀 Starting services..."

# Start backend
cd backend
echo "Starting FastAPI backend on port 8000..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend
cd frontend
echo "Starting React frontend on port 3000..."
REACT_APP_API_URL=http://localhost:8000 npm start &
FRONTEND_PID=$!
cd ..

echo "🎉 Alert Management System is running!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"

# Store PIDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

echo "✅ System ready for testing and demonstration!"
