#!/bin/bash

echo "🚀 Building Metrics Storage System"
echo "=================================="

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# Check if metrics-storage-system exists (created by setup.sh)
if [ ! -d "metrics-storage-system" ]; then
  echo "❌ metrics-storage-system not found. Run ./setup.sh first."
  exit 1
fi

cd metrics-storage-system
PROJECT="$ROOT/metrics-storage-system"

# Backend setup
echo "🐍 Setting up Python backend..."
cd backend
if [ -f "$PROJECT/venv/bin/activate" ]; then
  . "$PROJECT/venv/bin/activate"
  pip install -q -r requirements.txt 2>/dev/null || pip install -r requirements.txt
else
  python3 -m pip install -q -r requirements.txt 2>/dev/null || python3 -m pip install -r requirements.txt
fi
echo "✅ Backend dependencies installed"
cd ..

# Frontend setup
echo "⚛️  Setting up React frontend..."
cd frontend
npm install
echo "✅ Frontend dependencies installed"
cd ..

echo ""
echo "🎉 Build completed successfully!"
echo ""
echo "To run: ./start.sh"
echo "Demo:   ./run_demo.sh"
echo ""
