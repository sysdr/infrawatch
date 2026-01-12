#!/bin/bash

set -e

echo "=== Building User Management UI System ==="

# Backend setup
echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Frontend setup
echo "Setting up frontend..."
cd frontend
npm install
cd ..

echo "=== Build Complete ==="
echo ""
echo "To run without Docker:"
echo "  ./run.sh"
echo ""
echo "To run with Docker:"
echo "  docker-compose up --build"
