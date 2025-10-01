#!/bin/bash

echo "🚀 Building Alert Evaluation Engine"
echo "=================================="

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."
if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed."
    exit 1
fi

# Backend Setup
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

echo "✅ Backend dependencies installed"

# Frontend Setup
echo "⚛️  Setting up React frontend..."
cd ../frontend

# Install npm dependencies
npm install

echo "✅ Frontend dependencies installed"

# Return to root directory
cd ..

echo "🐳 Docker Setup (Optional)..."
if command_exists docker && command_exists docker-compose; then
    echo "✅ Docker and Docker Compose are available"
    echo "   You can run with Docker using: docker-compose -f docker/docker-compose.yml up"
else
    echo "⚠️  Docker not available - using local setup only"
fi

echo ""
echo "🎉 Build completed successfully!"
echo ""
echo "To run the application:"
echo "  1. Start backend: cd backend && source venv/bin/activate && python -m src.main"
echo "  2. Start frontend: cd frontend && npm start"
echo "  3. Or use Docker: docker-compose -f docker/docker-compose.yml up"
echo ""
echo "Application will be available at:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
