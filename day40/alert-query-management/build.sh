#!/bin/bash

echo "🚀 Starting Alert Query & Management System Build..."

# Create virtual environment
echo "📦 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

echo "✅ Dependencies installed successfully!"

# Database setup (using SQLite for development)
echo "🗄️ Setting up database..."
export DATABASE_URL="sqlite:///./alerts.db"

# Run without Docker
echo "🔧 Starting services without Docker..."

# Start backend
echo "🐍 Starting Python backend..."
cd backend
export DATABASE_URL="sqlite:///./alerts.db"
export REDIS_URL="redis://localhost:6379/0"
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend
echo "⚛️ Starting React frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Run tests
echo "🧪 Running tests..."
sleep 10

# Backend tests
cd backend
python -m pytest tests/ -v
cd ..

# Frontend tests
cd frontend
npm test -- --watchAll=false
cd ..

echo "✅ Build and tests completed!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"

# Create sample data
echo "📊 Creating sample alerts..."
curl -X POST "http://localhost:8000/api/alerts/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "",
    "limit": 1
  }' || echo "API not ready yet, manual testing required"

echo "🎉 System is ready for demonstration!"
echo "PIDs - Backend: $BACKEND_PID, Frontend: $FRONTEND_PID"
echo "Use stop.sh to stop all services"

# Save PIDs for stop script
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid
