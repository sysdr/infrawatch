#!/bin/bash
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "=== Building Metrics Storage System ==="

# Stop any existing services to avoid duplicates
if [ -f "$ROOT/stop.sh" ]; then
  "$ROOT/stop.sh" 2>/dev/null || true
fi
sleep 1

# Backend setup
echo "Setting up backend..."
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
if [ -f "venv/bin/activate" ]; then
  . venv/bin/activate
fi
pip install -q -r backend/requirements.txt 2>/dev/null || pip install -r backend/requirements.txt

# Run tests
echo "Running backend tests..."
cd backend
python3 -m pytest tests/ -v
cd "$ROOT"

# Frontend setup
echo "Setting up frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
  npm install
fi
cd "$ROOT"

# Start backend
echo "Starting backend..."
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
echo $! > "$ROOT/.backend.pid"
cd "$ROOT"

# Wait for backend, run demo to populate metrics
for i in 1 2 3 4 5 6 7 8 9 10; do
  if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null | grep -q 200; then
    echo "Backend ready. Running demo..."
    "$ROOT/run_demo.sh" http://localhost:8000
    break
  fi
  sleep 1
done

# Start frontend
echo "Starting frontend..."
cd frontend
(npm start 2>/dev/null || npx react-scripts start) &
echo $! > "$ROOT/.frontend.pid"
cd "$ROOT"

echo ""
echo "=== Build complete. System running ==="
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   Demo run - dashboard shows metrics"
echo ""
echo "To stop: $ROOT/stop.sh"
echo ""
