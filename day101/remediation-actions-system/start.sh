#!/bin/bash
# Single-server mode: backend serves API + dashboard at http://localhost:8000
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Stopping any existing services..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 1

# Build if needed
if [ ! -d "backend/venv" ]; then
  echo "Running build first..."
  ./build.sh
fi

# Build frontend if dist doesn't exist (optional)
if [ ! -d "frontend/dist" ] && [ -d "frontend/node_modules" ]; then
  echo "Building frontend..."
  cd frontend
  npm run build 2>/dev/null || node node_modules/vite/bin/vite.js build 2>/dev/null || true
  cd "$SCRIPT_DIR"
fi

echo "Starting backend..."
echo "Dashboard: http://localhost:8000/dashboard"
echo "API Docs: http://localhost:8000/docs"
cd backend
source venv/bin/activate
export DATABASE_URL="sqlite:///./remediation.db"
python init_db.py 2>/dev/null || true
uvicorn app.main:app --host 0.0.0.0 --port 8000
