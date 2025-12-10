#!/bin/bash

echo "=========================================="
echo "Building Export UI System"
echo "=========================================="

# Backend setup
echo "Setting up Python backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Frontend setup
echo "Setting up React frontend..."
cd frontend
npm install
cd ..

echo "Build complete!"
echo ""
echo "To start the system:"
echo "1. Local: ./run.sh"
echo "2. Docker: docker-compose up --build"
