#!/bin/bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# Stop any existing services first to avoid duplicates
if [ -f "$ROOT/stop.sh" ]; then
  "$ROOT/stop.sh" 2>/dev/null || true
fi
sleep 1

echo "🚀 Starting Metrics Storage System"

# Python deps (venv or system)
if [ ! -d "$ROOT/venv" ]; then
  python3 -m venv "$ROOT/venv"
fi
if [ -f "$ROOT/venv/bin/activate" ]; then
  . "$ROOT/venv/bin/activate"
  pip install -q -r "$ROOT/backend/requirements.txt" 2>/dev/null
else
  python3 -m pip install -q -r "$ROOT/backend/requirements.txt" 2>/dev/null
fi

# Backend
echo "Starting backend..."
cd "$ROOT/backend"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
echo $! > "$ROOT/.backend.pid"
cd "$ROOT"

# Wait for backend to be ready, then run demo (populates metrics for dashboard)
for i in 1 2 3 4 5 6 7 8 9 10; do
  if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null | grep -q 200; then
    echo "Backend ready. Running demo to populate metrics..."
    "$ROOT/run_demo.sh" http://localhost:8000
    break
  fi
  sleep 1
done

# Frontend
echo "Starting frontend..."
cd "$ROOT/frontend"
npm install --silent 2>/dev/null || npm install
(npm start 2>/dev/null || npx react-scripts start) &
echo $! > "$ROOT/.frontend.pid"
cd "$ROOT"

echo ""
echo "✅ System started!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   Demo already run - dashboard should show metrics"
echo "   Re-run demo: $ROOT/run_demo.sh"
echo ""
