#!/usr/bin/env bash
# =============================================================================
# Day 116: Stop containers and remove unused Docker resources
# Usage: ./cleanup.sh [--all]   --all = also remove day116 images and volumes
# =============================================================================
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[*] Stopping local services..."
pkill -f "uvicorn app.main" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
pkill -f "node.*day116" 2>/dev/null || true
sleep 1

echo "[*] Stopping Docker containers (day116 and compose)..."
docker compose down -v 2>/dev/null || true
docker stop $(docker ps -q --filter "name=day116") 2>/dev/null || true
docker rm $(docker ps -aq --filter "name=day116") 2>/dev/null || true

echo "[*] Removing unused Docker resources..."
docker system prune -f
docker volume prune -f
docker network prune -f

if [[ "$1" == "--all" ]]; then
  echo "[*] Removing day116 images..."
  docker rmi $(docker images -q --filter "reference=*day116*") 2>/dev/null || true
  docker image prune -af --filter "until=24h" 2>/dev/null || true
fi

echo "[*] Removing project artifacts (node_modules, dist, .venv, .pytest_cache, __pycache__, .pyc)..."
rm -rf "$SCRIPT_DIR/day116-caching/frontend/node_modules" 2>/dev/null || true
rm -rf "$SCRIPT_DIR/day116-caching/frontend/dist" 2>/dev/null || true
rm -rf "$SCRIPT_DIR/day116-caching/backend/.venv" 2>/dev/null || true
rm -rf "$SCRIPT_DIR/day116-caching/backend/.pytest_cache" 2>/dev/null || true
find "$SCRIPT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$SCRIPT_DIR" -name "*.pyc" -delete 2>/dev/null || true
echo "[*] Removing Istio-related files (if any)..."
find "$SCRIPT_DIR" -path "*istio*" -type f 2>/dev/null | while read -r f; do rm -f "$f" 2>/dev/null || true; done
find "$SCRIPT_DIR" -path "*istio*" -type d 2>/dev/null | sort -r | while read -r d; do rmdir "$d" 2>/dev/null || true; done

echo "[✓] Cleanup done."
