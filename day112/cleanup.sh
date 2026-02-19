#!/bin/bash
# Day 112: Force stop containers and remove unused Docker resources.
# Optionally stop local services and remove project artifacts (node_modules, venv, caches).
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="day112-analytics"

GREEN='\033[0;32m'; CYAN='\033[0;36m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${CYAN}[cleanup]${NC} $*"; }
ok()    { echo -e "${GREEN}✓${NC} $*"; }

# Force stop local app services
info "Stopping local services (force)..."
"$SCRIPT_DIR/stop.sh" 2>/dev/null || true
pkill -9 -f "uvicorn.*8112" 2>/dev/null || true
pkill -9 -f "vite.*3112" 2>/dev/null || true
lsof -ti :8112 | xargs -r kill -9 2>/dev/null || true
lsof -ti :3112 | xargs -r kill -9 2>/dev/null || true
ok "Local services stopped."

# Docker Compose down
if [ -d "$SCRIPT_DIR/$PROJECT" ]; then
  info "Docker Compose down..."
  (cd "$SCRIPT_DIR/$PROJECT" && docker compose down -v --remove-orphans -f 2>/dev/null) || true
  ok "Compose down."
fi

# Force stop and remove all containers
info "Stopping and removing all containers..."
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm -f $(docker ps -aq) 2>/dev/null || true
ok "Containers removed."

# Prune (force)
info "Pruning containers, networks, images, build cache..."
docker container prune -f
docker network prune -f
docker image prune -f
docker builder prune -f 2>/dev/null || true
ok "Docker pruned."

# Optional: all unused images
if [ "${1:-}" = "--all-images" ] || [ "${2:-}" = "--all-images" ]; then
  info "Removing all unused images..."
  docker image prune -a -f
  ok "All unused images removed."
fi

# Optional: remove project artifacts
if [ "${1:-}" = "--project" ] || [ "${2:-}" = "--project" ]; then
  info "Removing node_modules, venv, .pytest_cache, .pyc, Istio..."
  rm -rf "$SCRIPT_DIR/$PROJECT/frontend/node_modules"
  rm -rf "$SCRIPT_DIR/$PROJECT/venv"
  rm -rf "$SCRIPT_DIR/$PROJECT/backend/.pytest_cache"
  rm -rf "$SCRIPT_DIR/$PROJECT/backend/tests/.pytest_cache"
  find "$SCRIPT_DIR/$PROJECT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
  find "$SCRIPT_DIR/$PROJECT" -name "*.pyc" -delete 2>/dev/null || true
  find "$SCRIPT_DIR/$PROJECT" -type d -name "*istio*" -exec rm -rf {} + 2>/dev/null || true
  find "$SCRIPT_DIR/$PROJECT" -type f -path "*istio*" -delete 2>/dev/null || true
  ok "Project artifacts removed."
fi

echo ""
ok "Cleanup done. Use ./cleanup.sh --project to remove node_modules/venv/caches. Use --all-images to prune all images."
