#!/usr/bin/env bash
# =============================================================================
# Day 120: API Versioning — build.sh
# Build only: install deps, run tests, build frontend. Does not start services.
# Usage: ./build.sh
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
LOG_DIR="$SCRIPT_DIR/logs"
VENV_DIR="$SCRIPT_DIR/.venv"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'
log()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
err()  { echo -e "${RED}[✗]${NC} $*"; exit 1; }
info() { echo -e "${BLUE}[→]${NC} $*"; }
step() { echo -e "\n${CYAN}━━━ $* ${NC}"; }

mkdir -p "$LOG_DIR"

# Ensure sources exist
if [[ ! -f "$BACKEND_DIR/app/main.py" ]]; then
  err "Backend source missing. Run ../setup.sh from repo root first to generate project files."
fi
if [[ ! -f "$FRONTEND_DIR/package.json" ]]; then
  err "Frontend source missing. Run ../setup.sh from repo root first to generate project files."
fi

step "Python backend"
if [[ ! -d "$VENV_DIR" ]]; then
  info "Creating virtualenv..."
  python3 -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1090
. "$VENV_DIR/bin/activate"
pip install -q --upgrade pip
pip install -q -r "$BACKEND_DIR/requirements.txt"
log "Backend dependencies installed"

step "Backend tests"
cd "$BACKEND_DIR"
python -m pytest tests/ -v --tb=short 2>&1 | tee "$LOG_DIR/test-results.log"
cd "$SCRIPT_DIR"
log "Backend tests passed"

step "Frontend dependencies"
cd "$FRONTEND_DIR"
npm install --legacy-peer-deps --silent 2>&1 | tee "$LOG_DIR/npm-install.log" || warn "npm install had warnings — check $LOG_DIR/npm-install.log"
log "Frontend dependencies installed"

step "Frontend build"
if (cd "$FRONTEND_DIR" && npm run build 2>&1 | tee "$LOG_DIR/frontend-build.log"); then
  log "Frontend build complete"
else
  warn "Frontend build failed (see $LOG_DIR/frontend-build.log) — backend and tests OK"
fi
cd "$SCRIPT_DIR"
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   Build finished.                                     ${NC}"
echo -e "${GREEN}   Backend: ready to run (uvicorn)                      ${NC}"
if [[ -d "$FRONTEND_DIR/build" ]]; then
  echo -e "${GREEN}   Frontend: build output in $FRONTEND_DIR/build/     ${NC}"
else
  echo -e "${YELLOW}   Frontend: build skipped or failed — check logs       ${NC}"
fi
echo -e "${GREEN}   Start services: ./setup.sh                           ${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
