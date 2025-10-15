#!/bin/bash
set -e

echo "🚀 Building Alert System Integration..."

# Backend setup
echo "📦 Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Backend setup complete"

# Frontend setup
echo "📦 Setting up frontend..."
cd ../frontend
npm install
echo "✅ Frontend setup complete"

# Run tests
echo "🧪 Running backend tests..."
cd ../backend
source venv/bin/activate
pytest
echo "✅ Tests complete"

cd ..
echo "✅ Build complete!"
echo ""
echo "To start the application:"
echo "  Without Docker: ./start.sh"
echo "  With Docker: docker-compose up"
