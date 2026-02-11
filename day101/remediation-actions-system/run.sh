#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
echo "Starting Remediation Actions System..."

# Stop any existing services first
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 1

# Build if needed
if [ ! -d "backend/venv" ]; then
  echo "Running build first (venv missing)..."
  ./build.sh
fi

cd backend
source venv/bin/activate
export DATABASE_URL="sqlite:///./remediation.db"
export REDIS_URL="redis://localhost:6379"
python init_db.py
echo "Starting backend on port 8000..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
cd ..

sleep 3
cd frontend
if [ -d "node_modules" ]; then
  echo "Starting frontend on port 3000..."
  node node_modules/vite/bin/vite.js 2>/dev/null &
else
  echo "Frontend not built. Use dashboard at http://localhost:8000/dashboard"
fi
cd ..

echo ""
echo "System running!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "Dashboard (simple): http://localhost:8000/dashboard"
echo "Docs: http://localhost:8000/docs"
echo "Or run ./start.sh for single-server mode (dashboard at http://localhost:8000)"
echo "Run ./demo.sh to populate demo data"
echo ""
wait
