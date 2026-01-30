#!/bin/bash
# Start frontend only, using full path.
# HOST=0.0.0.0 so the dev server is reachable from the browser (avoids ERR_CONNECTION_REFUSED).
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
cd "$FRONTEND_DIR"
if [ ! -d node_modules ] || [ ! -f node_modules/.bin/react-scripts ]; then
  echo "Installing dependencies (npm install)..."
  npm install
fi
# Fix execute permission on .bin scripts (fixes "react-scripts: Permission denied" on WSL)
chmod -R +x node_modules/.bin 2>/dev/null || true
export HOST=0.0.0.0
export DANGEROUSLY_DISABLE_HOST_CHECK=true
exec npx react-scripts start
