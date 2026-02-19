#!/bin/bash
# Day 112: Build backend deps and frontend bundle (no Docker by default)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="day112-analytics"
BACKEND_ABS="$SCRIPT_DIR/$PROJECT/backend"
FRONTEND_ABS="$SCRIPT_DIR/$PROJECT/frontend"
VENV="$SCRIPT_DIR/$PROJECT/venv"

GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${CYAN}[build]${NC} $*"; }
ok()    { echo -e "${GREEN}✓${NC} $*"; }

if [ ! -d "$BACKEND_ABS" ] || [ ! -d "$FRONTEND_ABS" ]; then
  echo "Error: $PROJECT not found. Run ./setup.sh first."
  exit 1
fi

if [ "${1:-}" = "--docker" ]; then
  info "Building with Docker..."
  cd "$SCRIPT_DIR/$PROJECT"
  docker compose build
  ok "Docker images built."
  exit 0
fi

# Backend: ensure venv and deps
info "Backend: installing dependencies..."
if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV"
fi
"$VENV/bin/pip" install -q -r "$BACKEND_ABS/requirements.txt"
ok "Backend dependencies ready."

# Frontend: install and build
info "Frontend: npm install and build..."
cd "$FRONTEND_ABS"
npm install --silent
npm run build
ok "Frontend built (dist/)."

echo ""
ok "Build complete. Backend: $BACKEND_ABS  Frontend bundle: $FRONTEND_ABS/dist"
echo "  Run ./start.sh to start dev servers, or serve frontend from dist/."
