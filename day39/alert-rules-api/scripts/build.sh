#!/bin/bash

set -e

echo "🚀 Building Alert Rules API Project..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

echo "📦 Setting up Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🗄️ Initializing database..."
python -c "from app.models.database import init_db; import asyncio; asyncio.run(init_db())"

echo "🧪 Running backend tests..."
python -m pytest tests/ -v

echo "🌐 Installing frontend dependencies..."
cd ../frontend
npm install

echo "🧪 Running frontend tests..."
npm test -- --coverage --watchAll=false --passWithNoTests

echo "🏗️ Building frontend..."
npm run build

echo "✅ Build completed successfully!"
echo "🚀 To start the application:"
echo "   Backend: cd backend && source venv/bin/activate && python main.py"
echo "   Frontend: cd frontend && npm start"
echo "   Or use Docker: docker-compose up"
