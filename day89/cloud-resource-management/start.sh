#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=============================================="
echo "Cloud Resource Management - Startup"
echo "=============================================="

BACKEND_PORT=8001
API_URL="http://localhost:${BACKEND_PORT}"
export REACT_APP_API_URL="${API_URL}"

 dup_backend=$(pgrep -f "uvicorn app.main:app.*0.0.0.0:${BACKEND_PORT}" 2>/dev/null || true)
if [ -n "$dup_backend" ]; then
  echo "Backend already running on :${BACKEND_PORT}. Skipping."
else
  echo "Starting backend on :${BACKEND_PORT}..."
  (cd backend && python3 -m venv venv 2>/dev/null || true)
  (cd backend && . venv/bin/activate && pip install -q -r requirements.txt 2>/dev/null && uvicorn app.main:app --host 0.0.0.0 --port "${BACKEND_PORT}") &
  echo "Backend PID: $!"
  sleep 5
fi

if pgrep -f "react-scripts start" > /dev/null 2>&1; then
  echo "Frontend (react-scripts) already running. Skipping."
else
  echo "Starting frontend..."
  (cd frontend && npm install --silent 2>/dev/null && HOST=0.0.0.0 PORT=3000 REACT_APP_API_URL="${API_URL}" npm start) &
  echo "Frontend starting (may take a moment)..."
fi

echo ""
echo "Backend:  ${API_URL}"
echo "Frontend: http://localhost:3000"
echo "API docs: ${API_URL}/docs"
echo ""
echo "Run ./demo.sh to populate dashboard with sample data."
