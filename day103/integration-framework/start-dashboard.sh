#!/bin/bash
# Start only the backend and show the dashboard URL (no frontend).
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
"$ROOT/stop.sh" 2>/dev/null || true
sleep 1
if [ ! -d "$ROOT/venv" ]; then python3 -m venv "$ROOT/venv"; fi
. "$ROOT/venv/bin/activate" 2>/dev/null || true
pip install -q -r "$ROOT/backend/requirements.txt" 2>/dev/null
cd "$ROOT/backend"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
echo $! > "$ROOT/.backend.pid"
cd "$ROOT"
for i in $(seq 1 10); do
  if curl -s -o /dev/null http://127.0.0.1:8000/health 2>/dev/null; then
    "$ROOT/run_demo.sh" http://127.0.0.1:8000 2>/dev/null || true
    break
  fi
  sleep 1
done
echo ""
echo "=========================================="
echo "  Dashboard (open in browser):"
echo "  http://localhost:8000"
echo "  http://127.0.0.1:8000"
echo "=========================================="
echo "  Backend running. Press Ctrl+C to stop."
echo ""
