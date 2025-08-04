#!/bin/bash

echo "🚀 Starting Day 17: Server Validation & Health System"

# Check if services are already running
if [ -f backend.pid ] && ps -p $(cat backend.pid) > /dev/null 2>&1; then
    echo "⚠️  Backend is already running (PID: $(cat backend.pid))"
    echo "   Run ./stop.sh first to stop existing services"
    exit 1
fi

if [ -f frontend.pid ] && ps -p $(cat frontend.pid) > /dev/null 2>&1; then
    echo "⚠️  Frontend is already running (PID: $(cat frontend.pid))"
    echo "   Run ./stop.sh first to stop existing services"
    exit 1
fi

# Check if required tools are installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ Node.js/npm is not installed"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
if [ ! -f requirements.txt ]; then
    echo "❌ requirements.txt not found in backend directory"
    exit 1
fi
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install backend dependencies"
    exit 1
fi
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
if [ ! -f package.json ]; then
    echo "❌ package.json not found in frontend directory"
    exit 1
fi
npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install frontend dependencies"
    exit 1
fi
cd ..

# Start services
echo "🔧 Starting services..."

# Start Redis and PostgreSQL with Docker
echo "🐳 Starting Docker services..."
docker-compose up -d redis postgres
if [ $? -ne 0 ]; then
    echo "❌ Failed to start Docker services"
    exit 1
fi

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Start backend with proper virtual environment
echo "🚀 Starting backend server..."
cd backend
source ../venv/bin/activate
python -m app.main &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! ps -p $BACKEND_PID > /dev/null; then
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend
echo "🚀 Starting frontend development server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 5

# Check if frontend started successfully
if ! ps -p $FRONTEND_PID > /dev/null; then
    echo "❌ Frontend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ System started successfully!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"

# Store PIDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

echo ""
echo "📋 Services Status:"
echo "   Backend:  PID $BACKEND_PID (http://localhost:8000)"
echo "   Frontend: PID $FRONTEND_PID (http://localhost:3000)"
echo "   Docker:   Redis & PostgreSQL running"
echo ""
echo "💡 To stop all services, run: ./stop.sh"
echo "💡 To view logs, check the terminal output above"
echo ""
echo "Press Ctrl+C to stop all services"
wait
