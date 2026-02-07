#!/bin/bash
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
echo "🛑 Stopping services..."

for f in .backend.pid .frontend.pid; do
  if [ -f "$ROOT/$f" ]; then
    pid=$(cat "$ROOT/$f")
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      echo "Stopped PID $pid"
    fi
    rm -f "$ROOT/$f"
  fi
done

# Also kill any uvicorn on 8000 or node/react on 3000
pkill -f "uvicorn app.main" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true
echo "✅ Stopped"
