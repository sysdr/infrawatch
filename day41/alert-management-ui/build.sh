#!/bin/bash

echo "🚀 Building Alert Management UI System"
echo "====================================="

# Create virtual environment for backend
echo "📦 Setting up Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Start backend in background
echo "🐍 Starting FastAPI backend..."
cd app
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ../..

# Install and start frontend
echo "⚛️ Setting up React frontend..."
cd frontend
npm install

echo "🌐 Starting React frontend..."
npm start &
FRONTEND_PID=$!
cd ..

# Save PIDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

echo "✅ System started successfully!"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Run ./stop.sh to stop all services"

# Keep script running
wait
