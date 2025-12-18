#!/bin/bash

set -e

echo "======================================"
echo "Building Interactive Dashboard System"
echo "======================================"

# Navigate to project root
cd "$(dirname "$0")/.."

# Backend setup
echo "📦 Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Backend dependencies installed"

# Frontend setup
echo "📦 Setting up frontend..."
cd ../frontend
npm install
echo "✅ Frontend dependencies installed"

cd ..

echo "✅ Build complete!"
echo ""
echo "To run the application:"
echo "  1. Start PostgreSQL and Redis"
echo "  2. Run: ./scripts/start.sh"
