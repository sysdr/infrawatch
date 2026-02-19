#!/bin/bash
# Stop Day 112 Analytics backend and frontend (by PID file or by port)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="day112-analytics"
PID_FILE="$SCRIPT_DIR/$PROJECT/.pids"
BACKEND_PORT=8112
FRONTEND_PORT=3112

if [ -f "$PID_FILE" ]; then
  read -r BACKEND_PID FRONTEND_PID < "$PID_FILE" 2>/dev/null || true
  [ -n "$BACKEND_PID" ] && kill "$BACKEND_PID" 2>/dev/null || true
  [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null || true
  rm -f "$PID_FILE"
  echo "Stopped processes from PID file."
fi

for port in $BACKEND_PORT $FRONTEND_PORT; do
  pids=$(lsof -ti ":$port" 2>/dev/null || true)
  if [ -n "$pids" ]; then
    kill $pids 2>/dev/null || true
    echo "Killed process(es) on port $port"
  fi
done

echo "Day 112 services stopped."
