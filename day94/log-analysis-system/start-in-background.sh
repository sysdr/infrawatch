#!/bin/bash
# Start backend + frontend in background. Fixes "localhost refused to connect" / ERR_CONNECTION_REFUSED
# Run from log-analysis-system: ./start-in-background.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

echo "Stopping any existing services..."
"$SCRIPT_DIR/stop.sh" 2>/dev/null || true
sleep 2

echo ""
echo "Starting backend on port 8000..."
nohup "$SCRIPT_DIR/start_backend.sh" >> "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > .backend.pid

echo "Waiting for backend (up to 45 sec)..."
for i in $(seq 1 45); do
  if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
    echo "Backend is up."
    break
  fi
  sleep 1
  [ $i -eq 45 ] && echo "Backend may still be starting - check logs/backend.log"
done

echo ""
echo "Starting frontend on port 3001..."
cd "$SCRIPT_DIR/frontend"
[ ! -d "node_modules" ] && npm install
nohup env PORT=3001 HOST=0.0.0.0 npm start >> "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$SCRIPT_DIR/.frontend.pid"
cd "$SCRIPT_DIR"

echo ""
echo "=============================================="
echo "  OPEN IN BROWSER: http://localhost:3001"
echo "  (Wait 1–2 min for first compile, then refresh)"
echo "  Logs: logs/backend.log  logs/frontend.log"
echo "  To stop: ./stop.sh"
echo "=============================================="
