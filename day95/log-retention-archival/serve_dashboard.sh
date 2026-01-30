#!/bin/bash
# Serve the dashboard with Python's built-in HTTP server. No npm, no Docker.
# Open the URL shown below in your browser.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DASH_DIR="$SCRIPT_DIR/dashboard"
for PORT in 3000 3001 3002 3003; do
  if ! ss -tlnp 2>/dev/null | grep -q ":$PORT "; then
    break
  fi
done

cd "$DASH_DIR"
echo "Dashboard: http://localhost:$PORT"
echo "Press Ctrl+C to stop."
exec python3 -m http.server "$PORT"
