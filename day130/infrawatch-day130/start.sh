#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_PORT=8130
FRONTEND_PORT=3130

BACKEND_LOG="/tmp/infrawatch-backend-130.log"
FRONTEND_LOG="/tmp/infrawatch-frontend-130.log"
BACKEND_PID_FILE="/tmp/infrawatch-backend-130.pid"
FRONTEND_PID_FILE="/tmp/infrawatch-frontend-130.pid"

echo "[start] Root: $ROOT_DIR"

if [[ ! -d "$BACKEND_DIR" || ! -d "$FRONTEND_DIR" ]]; then
  echo "[start][error] backend/frontend directories not found."
  exit 1
fi

echo "[start] Stopping previous services on ports ${BACKEND_PORT}/${FRONTEND_PORT}..."
pkill -f "uvicorn.*${BACKEND_PORT}" 2>/dev/null || true
pkill -f "vite.*${FRONTEND_PORT}" 2>/dev/null || true
sleep 1

echo "[start] Starting backend..."
cd "$BACKEND_DIR"
if [[ ! -d ".venv" ]]; then
  echo "[start][error] .venv missing. Run ./build.sh first."
  exit 1
fi
source .venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload >"$BACKEND_LOG" 2>&1 &
echo $! >"$BACKEND_PID_FILE"

for i in {1..30}; do
  if curl -sf "http://localhost:${BACKEND_PORT}/health" >/dev/null; then
    echo "[start] Backend is healthy on :${BACKEND_PORT}"
    break
  fi
  sleep 1
  if [[ "$i" == "30" ]]; then
    echo "[start][error] Backend failed to become healthy. Check $BACKEND_LOG"
    exit 1
  fi
done

echo "[start] Starting frontend..."
cd "$FRONTEND_DIR"
nohup npm run dev >"$FRONTEND_LOG" 2>&1 &
echo $! >"$FRONTEND_PID_FILE"
sleep 3

echo "[start] Started."
echo "  Backend : http://localhost:${BACKEND_PORT}"
echo "  Frontend: http://localhost:${FRONTEND_PORT}"
echo "  Logs    : ${BACKEND_LOG} | ${FRONTEND_LOG}"
