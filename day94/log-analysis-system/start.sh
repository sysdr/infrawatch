#!/bin/bash
# Start backend and frontend - fixes "localhost refused to connect"
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Stopping any existing services..."
"$SCRIPT_DIR/stop.sh" 2>/dev/null || true
sleep 3

echo ""
echo "Starting backend on port 8000..."
"$SCRIPT_DIR/start_backend.sh" &
BACKEND_PID=$!
echo $BACKEND_PID > .backend.pid

echo "Waiting for backend (initial load ~15s, up to 60s)..."
sleep 5
for i in $(seq 1 55); do
  if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
    echo "Backend is up."
    break
  fi
  sleep 1
  [ $i -eq 55 ] && echo "Backend may still be starting - continuing anyway."
done

echo ""
echo "=============================================="
echo "  OPEN IN BROWSER: http://localhost:3001"
if [ -n "${WSL_DISTRO_NAME:-}" ] || grep -qi microsoft /proc/version 2>/dev/null; then
  WSL_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
  [ -n "$WSL_IP" ] && echo "  From Windows browser use: http://${WSL_IP}:3001"
fi
echo "  (Leave this terminal open)"
echo "=============================================="
echo ""
echo "Starting frontend (may take 1-2 min to compile)..."
"$SCRIPT_DIR/start_frontend.sh"
