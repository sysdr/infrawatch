#!/bin/bash
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
echo "Stopping services..."
for f in .backend.pid .frontend.pid; do
  if [ -f "$ROOT/$f" ]; then
    pid=$(cat "$ROOT/$f")
    kill -0 "$pid" 2>/dev/null && kill "$pid" 2>/dev/null
    rm -f "$ROOT/$f"
  fi
done
pkill -f "uvicorn app.main" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true
echo "Stopped"
