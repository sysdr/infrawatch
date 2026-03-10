#!/usr/bin/env bash
# =============================================================================
# Day 120: API Versioning — start.sh
# Start backend and frontend services only (no setup, no tests).
# Usage: ./start.sh
# Stop:  ./setup.sh stop
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

# Avoid duplicate services: stop any existing Day 120 processes
for pid_file in "$LOG_DIR/backend.pid" "$LOG_DIR/frontend.pid"; do
  if [[ -f "$pid_file" ]]; then
    pid=$(cat "$pid_file" 2>/dev/null)
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
    rm -f "$pid_file"
  fi
done
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true

step "Starting services"

if [[ ! -f "$BACKEND_DIR/app/main.py" ]]; then
  err "Backend source missing. Run ../setup.sh from repo root first to generate project files."
fi
if [[ ! -f "$FRONTEND_DIR/package.json" ]]; then
  err "Frontend source missing. Run ../setup.sh from repo root first to generate project files."
fi

# Backend
. "$VENV_DIR/bin/activate"
cd "$BACKEND_DIR"
nohup "$VENV_DIR/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8000 --reload \
  > "$LOG_DIR/backend.log" 2>&1 &
echo $! > "$LOG_DIR/backend.pid"
cd "$SCRIPT_DIR"
sleep 3
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
  log "Backend  → http://localhost:8000"
  log "API Docs → http://localhost:8000/docs"
else
  warn "Backend still starting — check $LOG_DIR/backend.log"
fi

# Frontend
if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  info "Installing npm packages (first run — may take a minute)..."
  (cd "$FRONTEND_DIR" && npm install --legacy-peer-deps) > "$LOG_DIR/npm-install.log" 2>&1 \
    || warn "npm install had warnings — check $LOG_DIR/npm-install.log"
fi
cd "$FRONTEND_DIR"
BROWSER=none nohup npm start > "$LOG_DIR/frontend.log" 2>&1 &
echo $! > "$LOG_DIR/frontend.pid"
cd "$SCRIPT_DIR"
sleep 5
log "Frontend → http://localhost:3000"

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   Day 120 — services started                          ${NC}"
echo -e "${GREEN}   Dashboard  → http://localhost:8000/dashboard        ${NC}"
echo -e "${GREEN}   API Docs   → http://localhost:8000/docs              ${NC}"
echo -e "${GREEN}   Logs       → $LOG_DIR/                              ${NC}"
echo -e "${GREEN}   Stop all   → ./setup.sh stop  (from repo root)        ${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
