#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "Starting Correlation Analysis System"
echo "=========================================="

# Free ports so this run can bind (avoid EADDRINUSE / stale processes)
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 3000/tcp 2>/dev/null || true
sleep 2

# Only warn about PostgreSQL if user explicitly set DATABASE_URL to use it
if [ -n "$DATABASE_URL" ] && command -v pg_isready >/dev/null 2>&1; then
  if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "PostgreSQL not ready on 5432. Start it or unset DATABASE_URL to use SQLite."
  fi
fi

# Start backend
echo "Starting backend..."
cd "$PROJECT_ROOT/backend"
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Resolve Node (nvm often not loaded in script context)
NODE=""
if command -v node >/dev/null 2>&1; then
  NODE="$(command -v node)"
else
  export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
  if [ -s "$NVM_DIR/nvm.sh" ]; then
    set +e
    . "$NVM_DIR/nvm.sh"
    [ -f "$PROJECT_ROOT/frontend/.nvmrc" ] && nvm use 2>/dev/null || nvm use 20 2>/dev/null || true
    set -e
    NODE="$(command -v node 2>/dev/null)" || true
  fi
  [ -z "$NODE" ] && [ -x "$NVM_DIR/versions/node/v20.20.0/bin/node" ] && NODE="$NVM_DIR/versions/node/v20.20.0/bin/node"
  [ -z "$NODE" ] && [ -x "$HOME/.nvm/versions/node/v20.20.0/bin/node" ] && NODE="$HOME/.nvm/versions/node/v20.20.0/bin/node"
fi
if [ -z "$NODE" ] || [ ! -x "$NODE" ]; then
  echo "ERROR: node not found. Install Node.js (e.g. nvm install 20) and try again."
  exit 1
fi

echo "Starting frontend (Node: $NODE)..."
cd "$PROJECT_ROOT/frontend"
BROWSER=none "$NODE" node_modules/react-scripts/bin/react-scripts.js start &
FRONTEND_PID=$!

echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Waiting for frontend to compile (up to 120s)..."
FRONTEND_READY=""
for i in $(seq 1 60); do
  if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 http://127.0.0.1:3000 2>/dev/null | grep -q 200; then
    FRONTEND_READY=1
    break
  fi
  sleep 2
done
if [ -n "$FRONTEND_READY" ]; then
  echo ""
  echo "Compiled successfully! Open in your browser:"
  echo "  http://localhost:3000"
  echo "  http://127.0.0.1:3000"
  echo ""
else
  echo ""
  echo "Frontend may still be compiling. Open when ready: http://localhost:3000"
  echo ""
fi
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
wait
