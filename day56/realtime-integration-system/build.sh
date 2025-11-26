#!/bin/bash

echo "🔨 Building Real-time Integration System..."

# Backend setup
echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend ready"
cd ..

# Frontend setup
echo "Setting up frontend..."
cd frontend
npm install

echo "✅ Frontend ready"
cd ..

echo "✨ Build complete!"
echo ""
echo "To start without Docker:"
echo "1. Terminal 1: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "2. Terminal 2: cd frontend && npm start"
echo ""
echo "To start with Docker:"
echo "docker-compose up --build"
