#!/bin/bash
# Day 113: Build backend deps and frontend bundle (no Docker by default)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
BACKEND_ABS="$PROJECT_DIR/backend"
FRONTEND_ABS="$PROJECT_DIR/frontend"
VENV="$BACKEND_ABS/.venv"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'
info()  { echo -e "${CYAN}[build]${NC} $*"; }
ok()    { echo -e "${GREEN}✓${NC} $*"; }

if [ ! -d "$BACKEND_ABS" ] || [ ! -d "$FRONTEND_ABS" ]; then
  echo "Error: backend/frontend not found. Run ../setup.sh from day113 root first."
  exit 1
fi

if [ "${1:-}" = "--docker" ]; then
  info "Building with Docker..."
  cd "$PROJECT_DIR/docker"
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

# Frontend: install and build (if node available)
if command -v node &>/dev/null; then
  info "Frontend: npm install and build..."
  cd "$FRONTEND_ABS"
  npm install --legacy-peer-deps --silent
  npm run build
  ok "Frontend built (build/)."
else
  echo -e "${YELLOW}[build]${NC} Node.js not found — skipping frontend build."
fi

echo ""
ok "Build complete. Backend: $BACKEND_ABS   Frontend: $FRONTEND_ABS"
echo "  Run ./start.sh to start services, or ../setup.sh --stop from day113 root to stop."
