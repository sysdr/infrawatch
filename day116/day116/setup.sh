#!/usr/bin/env bash
# =============================================================================
# Day 116: Caching Systems — Setup launcher
# Run from day116/: ./setup.sh (local) or ./setup.sh --docker
# Ensures full paths, duplicate-service check, then runs tests and startup.
# =============================================================================
set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BLUE='\033[0;34m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
log()  { echo -e "${GREEN}[✓]${NC} $*"; }
info() { echo -e "${BLUE}[→]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
error(){ echo -e "${RED}[✗]${NC} $*"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/day116-caching"

# Required files (from original generator)
REQUIRED_FILES=(
  backend/requirements.txt backend/app/main.py backend/app/models/__init__.py
  backend/app/cache/__init__.py backend/app/cache/redis_cache.py backend/app/api/__init__.py
  backend/app/api/cache_routes.py backend/tests/test_cache.py
)
# Check for full generator script first
FULL_SETUP="$SCRIPT_DIR/setup_full.sh"
if [ ! -f "$PROJECT_DIR/backend/app/main.py" ] && [ -f "$FULL_SETUP" ]; then
  info "Running full setup to generate project files..."
  bash "$FULL_SETUP" "$@"
  exit $?
fi
if [ ! -f "$PROJECT_DIR/backend/app/main.py" ]; then
  warn "Project not generated. Ensure the full 1890-line setup script is saved to day116/setup.sh (or as setup_full.sh) and run it; or use: ./setup.sh --docker"
  error "Missing: $PROJECT_DIR/backend/app/main.py"
fi
# Verify required files
MISSING=()
for f in "${REQUIRED_FILES[@]}"; do
  [ -f "$PROJECT_DIR/$f" ] || MISSING+=("$f")
done
if [ ${#MISSING[@]} -gt 0 ]; then
  warn "Missing files: ${MISSING[*]}"
fi

# Duplicate-service check
EXISTING=$(pgrep -f "uvicorn app.main:app" 2>/dev/null | wc -l)
if [ "${EXISTING:-0}" -gt 0 ]; then
  warn "Stopping $EXISTING existing uvicorn process(es)..."
  pkill -f "uvicorn app.main:app" 2>/dev/null || true
  sleep 2
fi

BACKEND_VENV="$PROJECT_DIR/backend/.venv"
[ -d "$BACKEND_VENV" ] || { info "Creating venv..."; python3 -m venv "$BACKEND_VENV"; "$BACKEND_VENV/bin/pip" install -q -r "$PROJECT_DIR/backend/requirements.txt"; }
info "Starting backend (full path)..."
(cd "$PROJECT_DIR/backend" && REDIS_URL="${REDIS_URL:-redis://localhost:6379}" "$BACKEND_VENV/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8000 --log-level warning) &
echo $! > /tmp/day116_backend.pid
sleep 3
curl -sf http://localhost:8000/health >/dev/null || error "Backend not ready"
log "Backend up (PID $(cat /tmp/day116_backend.pid))"
info "Running tests..."
(cd "$PROJECT_DIR/backend" && REDIS_URL="${REDIS_URL:-redis://localhost:6379}" "$BACKEND_VENV/bin/pytest" tests/ -v --tb=short --no-header) || true
log "Done. Dashboard: http://localhost:3000 (start frontend from $PROJECT_DIR/frontend with: npm run dev)"
