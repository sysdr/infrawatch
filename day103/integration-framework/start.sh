#!/bin/bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# Stop any existing services first (avoid duplicates)
if [ -f "$ROOT/stop.sh" ]; then
  "$ROOT/stop.sh" 2>/dev/null || true
fi
sleep 1

echo "Starting Integration Framework..."
if [ ! -d "$ROOT/venv" ]; then python3 -m venv "$ROOT/venv"; fi
. "$ROOT/venv/bin/activate" 2>/dev/null || true
pip install -q -r "$ROOT/backend/requirements.txt" 2>/dev/null

echo "Starting backend..."
cd "$ROOT/backend"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
echo $! > "$ROOT/.backend.pid"
cd "$ROOT"

for i in $(seq 1 10); do
  if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null | grep -q 200 2>/dev/null; then
    echo "Backend ready. Running demo..."
    "$ROOT/run_demo.sh" http://localhost:8000
    break
  fi
  sleep 1
done

echo "Starting frontend..."
cd "$ROOT/frontend"
npm install --silent 2>/dev/null || npm install
(npm start 2>/dev/null || npx react-scripts start) &
echo $! > "$ROOT/.frontend.pid"
cd "$ROOT"

echo ""
echo "Dashboard: http://localhost:3000"
echo "Backend:   http://localhost:8000"
echo "Re-run demo: $ROOT/run_demo.sh"
echo ""
