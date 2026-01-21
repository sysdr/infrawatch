#!/bin/bash

set -e

echo "============================================"
echo "Building Container Monitoring System"
echo "============================================"

# Build backend
echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Build frontend
echo "Setting up frontend..."
cd frontend
npm install
cd ..

echo ""
echo "============================================"
echo "Build completed successfully!"
echo "============================================"
echo ""
echo "To run the application:"
echo ""
echo "Option 1: With Docker"
echo "  docker-compose -f docker/docker-compose.yml up"
echo ""
echo "Option 2: Without Docker"
echo "  Terminal 1: cd backend && source venv/bin/activate && uvicorn backend.app.main:app --reload"
echo "  Terminal 2: cd frontend && npm run dev"
echo ""
echo "Dashboard will be available at: http://localhost:3000"
echo "API docs at: http://localhost:8000/docs"
