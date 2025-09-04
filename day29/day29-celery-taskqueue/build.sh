#!/bin/bash

set -e

echo "🚀 Building Day 29: Celery Task Queue System"

# Setup Python virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install frontend dependencies
echo "⚛️ Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "✅ Build completed successfully!"
echo ""
echo "To run the system:"
echo "1. Start Redis: docker run --name redis -p 6379:6379 -d redis:7.2-alpine"
echo "2. Start backend: source venv/bin/activate && python app/run.py"
echo "3. Start workers: source venv/bin/activate && python worker/start_worker.py"
echo "4. Start frontend: cd frontend && npm start"
echo "5. Open dashboard: http://localhost:3000"
echo ""
echo "Or use Docker: docker-compose up --build"
