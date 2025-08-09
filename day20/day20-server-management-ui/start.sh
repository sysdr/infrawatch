#!/bin/bash
set -e

echo "🚀 Starting Day 20: Server Management UI"

# Create Python virtual environment
echo "📦 Setting up Python virtual environment..."
cd backend
if [ ! -d venv ]; then
  python3 -m venv venv
fi
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Start backend in background (uvicorn)
echo "🔧 Starting Python backend..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

cd ../frontend

# Install Node.js dependencies if needed
echo "📥 Installing Node.js dependencies..."
if [ ! -d node_modules ]; then
  npm install
fi

# Start frontend
echo "🌐 Starting React frontend..."
export BROWSER=none
npm start &
FRONTEND_PID=$!

echo "✅ Application started successfully!"
echo "Backend running on: http://localhost:8000"
echo "Frontend running on: http://localhost:3000"
echo "API docs available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup processes
cleanup() {
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Trap interrupt signal
trap cleanup INT

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
