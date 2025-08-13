#!/bin/bash

echo "🚀 Starting Server Management Integration System"
echo "================================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed"
    exit 1
fi

echo "✅ Dependencies check passed"

# Backend setup
echo "🐍 Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend dependencies installed"

# Start backend in background
echo "🔄 Starting backend server..."
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid

# Wait for backend to start
sleep 5

# Frontend setup
echo "⚛️ Setting up frontend..."
cd ../frontend

# Install dependencies
npm install

echo "✅ Frontend dependencies installed"

# Build frontend
echo "🔨 Building frontend..."
npm run build

# Start frontend in background
echo "🔄 Starting frontend server..."
nohup npm start > frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > frontend.pid

# Wait for frontend to start
sleep 10

echo "✅ System startup complete!"
echo ""
echo "🌐 Backend API: http://localhost:8000"
echo "🌐 Frontend Dashboard: http://localhost:3000"
echo "📊 API Health Check: http://localhost:8000/health"
echo ""
echo "📋 Running tests..."

cd ../backend
source venv/bin/activate
python -m pytest tests/ -v

cd ../frontend
npm test -- --watchAll=false

echo ""
echo "🎉 Server Management Integration is ready!"
echo "   Open http://localhost:3000 in your browser"
echo ""
echo "💡 To stop the system, run: ./stop.sh"
