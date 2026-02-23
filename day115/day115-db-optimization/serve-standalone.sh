#!/usr/bin/env bash
# Serve standalone dashboard (no React build required). Use when npm start fails.
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PUBLIC="$SCRIPT_DIR/frontend/public"
PORT="${FRONTEND_PORT:-3000}"
# Free port if in use
fuser -k "$PORT/tcp" 2>/dev/null || true
sleep 1
echo "Serving DB Optimization Dashboard at http://localhost:$PORT/"
echo "Open in your browser: http://localhost:$PORT/"
echo "Press Ctrl+C to stop."
cd "$PUBLIC"
exec python3 -m http.server "$PORT"
