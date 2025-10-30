#!/bin/bash

echo "🚀 Building Day 46: Notification Preferences System"
echo "=================================================="

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate || . venv/Scripts/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Setup database (using SQLite for development)
echo "🗄️  Setting up database..."
export DATABASE_URL="sqlite:///./notifications.db"

# Run database migrations
cd backend
python -c "
from models.base import Base
from config.database import engine
Base.metadata.create_all(bind=engine)
print('✅ Database tables created')
"
cd ..

# Build frontend
echo "🏗️  Building frontend..."
cd frontend
npm run build
cd ..

echo "✅ Build completed successfully!"

# Run tests
echo "🧪 Running tests..."
cd backend
python -m pytest ../tests/ -v
cd ..

echo "🎯 Starting services..."

# Start backend in background
echo "🚀 Starting backend server..."
cd backend
export DATABASE_URL="sqlite:///./notifications.db"
export PYTHONPATH=$PWD
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend in background  
echo "🌐 Starting frontend development server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "🎉 Services started successfully!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "✋ Press Ctrl+C to stop all services"

# Save PIDs for stop script
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

# Wait for user interrupt
wait
