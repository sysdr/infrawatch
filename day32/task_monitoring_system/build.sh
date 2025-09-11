#!/bin/bash

echo "🚀 Building Task Monitoring System"
echo "=================================="

# Check if running with Docker flag
if [[ "$1" == "--docker" ]]; then
    echo "🐳 Building with Docker..."
    
    # Build and start with Docker Compose
    docker-compose down
    docker-compose build
    docker-compose up -d
    
    echo "✅ Docker containers started"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔗 Backend API: http://localhost:8000"
    echo "📊 API Docs: http://localhost:8000/docs"
    
    exit 0
fi

# Local development build
echo "💻 Building for local development..."

# Backend setup
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate || source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app.utils.database import init_database; init_database()"

# Start backend in background
echo "🚀 Starting backend server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

cd ..

# Frontend setup
echo "⚛️ Setting up React frontend..."
cd frontend

# Install dependencies
npm install

# Start frontend in background
echo "🚀 Starting frontend server..."
npm start &
FRONTEND_PID=$!

cd ..

# Store PIDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

echo ""
echo "✅ Build complete!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
echo ""
echo "🧪 Running tests..."

# Run backend tests
cd backend
source venv/bin/activate || source venv/Scripts/activate
python -m pytest tests/ -v
cd ..

echo ""
echo "🎉 All systems ready!"
echo "💡 Use './stop.sh' to stop all services"
