#!/usr/bin/env bash
# Day 116: Start backend (and frontend if present). Uses full paths, checks for duplicates.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/day116-caching"
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
log()  { echo -e "${GREEN}[✓]${NC} $*"; }
info() { echo -e "${BLUE}[→]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }

# Duplicate check: stop existing uvicorn
EXISTING=$(pgrep -f "uvicorn app.main:app" 2>/dev/null | wc -l)
if [ "${EXISTING:-0}" -gt 0 ]; then
  warn "Stopping $EXISTING existing uvicorn process(es)..."
  pkill -f "uvicorn app.main:app" 2>/dev/null || true
  sleep 2
fi

# Backend
[ -d "$PROJECT_DIR/backend/.venv" ] || { echo "Run ./build.sh first."; exit 1; }
info "Starting backend..."
(cd "$PROJECT_DIR/backend" && REDIS_URL="${REDIS_URL:-redis://localhost:6379}" "$PROJECT_DIR/backend/.venv/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8000 --log-level warning) &
echo $! > /tmp/day116_backend.pid
for i in 1 2 3 4 5 6 7 8 9 10; do
  sleep 2
  curl -sf http://localhost:8000/health >/dev/null && break
  [ "$i" -eq 10 ] && { echo "Backend failed to become ready (check Redis and logs)."; exit 1; }
done
log "Backend ready (PID $(cat /tmp/day116_backend.pid)) — http://localhost:8000"

# Frontend (optional)
if command -v node >/dev/null 2>&1 && [ -f "$PROJECT_DIR/frontend/package.json" ]; then
  info "Starting frontend..."
  (cd "$PROJECT_DIR/frontend" && npm run dev) &
  echo $! > /tmp/day116_frontend.pid
  sleep 2
  log "Frontend started (PID $(cat /tmp/day116_frontend.pid)) — http://localhost:3000"
else
  echo "Frontend not started (no package.json or node)."
fi

log "Done. API: http://localhost:8000  Docs: http://localhost:8000/docs"
