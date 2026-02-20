#!/usr/bin/env bash
# Day 113: Stop containers and remove unused Docker resources, containers, and images
# Also removes node_modules, venv, .pytest_cache, .pyc, and Istio artifacts
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'
log()  { echo -e "${GREEN}[cleanup]${NC} $*"; }
info() { echo -e "${CYAN}[cleanup]${NC} $*"; }
warn() { echo -e "${YELLOW}[cleanup]${NC} $*"; }

# Remove project artifacts (node_modules, venv, .pytest_cache, .pyc, Istio)
if [ -d "$PROJECT_DIR" ]; then
  info "Removing project artifacts..."
  rm -rf "$PROJECT_DIR/frontend/node_modules"
  rm -rf "$PROJECT_DIR/backend/.venv"
  rm -rf "$PROJECT_DIR/backend/venv"
  find "$PROJECT_DIR" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
  find "$PROJECT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
  find "$PROJECT_DIR" -name "*.pyc" -type f -delete 2>/dev/null || true
  find "$SCRIPT_DIR" -maxdepth 3 -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
  find "$SCRIPT_DIR" -maxdepth 3 -type d -name ".venv" -exec rm -rf {} + 2>/dev/null || true
  find "$SCRIPT_DIR" -maxdepth 3 -iname "*istio*" -exec rm -rf {} + 2>/dev/null || true
  log "Artifacts removed (node_modules, venv, .pytest_cache, __pycache__, .pyc, Istio)."
fi

# Stop Day 113 app services (FastAPI, React)
if [ -f /tmp/day113_backend.pid ]; then
  PID=$(cat /tmp/day113_backend.pid)
  kill "$PID" 2>/dev/null && log "Stopped FastAPI (pid $PID)" || true
  rm -f /tmp/day113_backend.pid
fi
if [ -f /tmp/day113_frontend.pid ]; then
  PID=$(cat /tmp/day113_frontend.pid)
  kill "$PID" 2>/dev/null && log "Stopped React (pid $PID)" || true
  pkill -f "react-scripts start" 2>/dev/null || true
  rm -f /tmp/day113_frontend.pid
fi

# Stop Docker Compose project (day113)
if [ -f "$PROJECT_DIR/docker/docker-compose.yml" ]; then
  info "Stopping Docker Compose (day113)..."
  cd "$PROJECT_DIR/docker"
  docker compose down -v 2>/dev/null && log "Containers and volumes stopped" || warn "Docker compose down failed or not running"
  cd "$SCRIPT_DIR"
fi

# Remove stopped day113 containers
info "Removing day113 containers..."
docker ps -aq --filter "name=day113" 2>/dev/null | xargs -r docker rm -f 2>/dev/null || true
log "Day 113 containers removed"

# Remove unused Docker resources
if [ "${1:-}" = "--all" ]; then
  info "Docker system prune (containers, networks, images, build cache)..."
  docker system prune -af --volumes 2>/dev/null && log "Docker system prune done" || warn "Docker prune failed"
else
  info "Removing dangling images and build cache (use --all for full system prune)..."
  docker image prune -f 2>/dev/null || true
  docker builder prune -f 2>/dev/null || true
  log "Docker cleanup done (run ./cleanup.sh --all to prune everything)."
fi

log "Cleanup complete."
