#!/bin/bash
ROOT="$(cd "$(dirname "$0")" && pwd)"
for port in 8000 3000; do
  pid=$(lsof -ti:$port 2>/dev/null) || true
  if [ -n "$pid" ]; then kill $pid 2>/dev/null; fi
done
[ -f "$ROOT/backend.pid" ] && kill $(cat "$ROOT/backend.pid") 2>/dev/null; rm -f "$ROOT/backend.pid"
[ -f "$ROOT/frontend.pid" ] && kill $(cat "$ROOT/frontend.pid") 2>/dev/null; rm -f "$ROOT/frontend.pid"
echo "Stopped."
