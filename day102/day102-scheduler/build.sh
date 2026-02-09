#!/bin/bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "=== Building Scheduler System ==="
if [ -f "$ROOT/stop.sh" ]; then "$ROOT/stop.sh" 2>/dev/null || true; fi
sleep 1

echo "Setting up backend..."
if [ ! -d "venv" ]; then python3 -m venv venv; fi
. venv/bin/activate 2>/dev/null || true
pip install -q -r backend/requirements.txt 2>/dev/null || pip install -r backend/requirements.txt

echo "Running backend tests..."
cd backend && export DATABASE_URL="sqlite:///./test.db" && python3 -m pytest tests/ -v && cd "$ROOT"

echo "Setting up frontend..."
cd frontend && [ ! -d "node_modules" ] && npm install && cd "$ROOT" || cd "$ROOT"

echo "Starting backend..."
cd backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
echo $! > "$ROOT/.backend.pid"
cd "$ROOT"

for i in $(seq 1 10); do
  if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null | grep -q 200; then
    echo "Backend ready. Running demo..."
    "$ROOT/run_demo.sh" http://localhost:8000
    break
  fi
  sleep 1
done

echo "Starting frontend..."
cd frontend && (npm start 2>/dev/null || npx react-scripts start) &
echo $! > "$ROOT/.frontend.pid"
cd "$ROOT"

echo ""
echo "=== Build complete. System running ==="
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   To stop: $ROOT/stop.sh"
echo ""
