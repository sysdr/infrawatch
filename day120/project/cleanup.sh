#!/usr/bin/env bash
# =============================================================================
# Day 120 — cleanup.sh
# Stop all services and Docker resources; remove local build/cache artifacts.
# Usage: ./cleanup.sh              # full cleanup
#        ./cleanup.sh --dry-run   # show what would be removed/stopped
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
DRY_RUN=false

for arg in "$@"; do
  [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log()  { echo -e "${GREEN}[✓]${NC} $*"; }
info() { echo -e "${YELLOW}[→]${NC} $*"; }

# -----------------------------------------------------------------------------
# 1. Stop Day 120 services (backend, frontend)
# -----------------------------------------------------------------------------
info "Stopping Day 120 services..."
if [[ -f "$LOG_DIR/backend.pid" ]]; then
  pid=$(cat "$LOG_DIR/backend.pid" 2>/dev/null)
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    $DRY_RUN || kill "$pid" 2>/dev/null
    $DRY_RUN && echo "  would stop backend PID $pid" || log "Stopped backend PID $pid"
  fi
  $DRY_RUN || rm -f "$LOG_DIR/backend.pid"
fi
if [[ -f "$LOG_DIR/frontend.pid" ]]; then
  pid=$(cat "$LOG_DIR/frontend.pid" 2>/dev/null)
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    $DRY_RUN || kill "$pid" 2>/dev/null
    $DRY_RUN && echo "  would stop frontend PID $pid" || log "Stopped frontend PID $pid"
  fi
  $DRY_RUN || rm -f "$LOG_DIR/frontend.pid"
fi
$DRY_RUN || { pkill -f "uvicorn app.main:app" 2>/dev/null || true; pkill -f "react-scripts start" 2>/dev/null || true; }
$DRY_RUN && echo "  would pkill uvicorn/react-scripts" || log "Day 120 processes stopped"

# -----------------------------------------------------------------------------
# 2. Stop Docker Compose (this project) and all containers
# -----------------------------------------------------------------------------
info "Stopping Docker containers and cleaning Docker resources..."
if [[ -f "$REPO_ROOT/docker-compose.yml" ]]; then
  $DRY_RUN && echo "  would run: docker compose down --remove-orphans (from repo root)" || (cd "$REPO_ROOT" && docker compose down --remove-orphans 2>/dev/null) && log "Docker Compose down" || true
fi
if $DRY_RUN; then
  echo "  would run: docker stop \$(docker ps -aq) and docker rm"
else
  ids=$(docker ps -aq 2>/dev/null)
  if [[ -n "$ids" ]]; then
    docker stop $ids 2>/dev/null || true
    docker rm $ids 2>/dev/null || true
    log "Docker containers stopped/removed"
  else
    log "No Docker containers to stop"
  fi
fi

# -----------------------------------------------------------------------------
# 3. Remove unused Docker resources (images, networks, build cache)
# -----------------------------------------------------------------------------
$DRY_RUN && echo "  would run: docker image prune -af" || docker image prune -af 2>/dev/null || true
$DRY_RUN && echo "  would run: docker network prune -f" || docker network prune -f 2>/dev/null || true
$DRY_RUN && echo "  would run: docker builder prune -af" || docker builder prune -af 2>/dev/null || true
$DRY_RUN && echo "  would run: docker system prune -af (optional)" || true
# Uncomment next line for full system prune (removes all unused images/containers/networks/volumes):
# docker system prune -af --volumes 2>/dev/null || true
log "Docker unused resources pruned"

# -----------------------------------------------------------------------------
# 4. Remove project artifacts (node_modules, venv, caches, .pyc)
# -----------------------------------------------------------------------------
info "Removing project build/cache artifacts..."

remove_if_exists() {
  local path="$1"
  if [[ -e "$path" ]]; then
    if $DRY_RUN; then echo "  would remove: $path"; else rm -rf "$path"; log "Removed $path"; fi
  fi
}

remove_if_exists "$SCRIPT_DIR/node_modules"
remove_if_exists "$FRONTEND_DIR/node_modules"
remove_if_exists "$SCRIPT_DIR/.venv"
remove_if_exists "$BACKEND_DIR/.pytest_cache"
remove_if_exists "$BACKEND_DIR/tests/.pytest_cache"

# __pycache__ and .pyc under backend (only in project source, not inside .venv)
if [[ -d "$BACKEND_DIR" ]]; then
  if $DRY_RUN; then
    find "$BACKEND_DIR" -type d -name "__pycache__" 2>/dev/null | while read -r d; do echo "  would remove: $d"; done
    find "$BACKEND_DIR" -name "*.pyc" 2>/dev/null | while read -r f; do echo "  would remove: $f"; done
  else
    find "$BACKEND_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$BACKEND_DIR" -name "*.pyc" -delete 2>/dev/null || true
    log "Removed __pycache__ and .pyc under backend"
  fi
fi

# Istio-related files/dirs (if any in project)
find "$SCRIPT_DIR" -maxdepth 3 \( -type d -name "*istio*" -o -type f -name "*istio*" \) 2>/dev/null | while read -r path; do remove_if_exists "$path"; done

# Optional: remove frontend build output
# remove_if_exists "$FRONTEND_DIR/build"

# Optional: remove logs (uncomment if desired)
# remove_if_exists "$LOG_DIR"

echo ""
echo -e "${GREEN}Cleanup finished.${NC} Re-run ../setup.sh (from repo root) or ./build.sh to recreate venv and node_modules."
echo ""
