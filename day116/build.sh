#!/usr/bin/env bash
# Day 116: Build backend (venv + deps) and frontend (npm install + build)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/day116-caching"
GREEN='\033[0;32m'; BLUE='\033[0;34m'; NC='\033[0m'
log()  { echo -e "${GREEN}[✓]${NC} $*"; }
info() { echo -e "${BLUE}[→]${NC} $*"; }

# Backend
info "Building backend..."
cd "$PROJECT_DIR/backend"
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt
log "Backend deps installed"

# Frontend (if present)
if [ -f "$PROJECT_DIR/frontend/package.json" ]; then
  info "Building frontend..."
  cd "$PROJECT_DIR/frontend"
  npm install --silent
  npm run build
  log "Frontend built"
else
  echo "No frontend/package.json — skipping frontend build"
fi

log "Build complete."
