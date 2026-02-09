#!/bin/bash
# Day 102: Stop containers and remove unused Docker resources, containers, images

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "=== Stopping services ==="
if [ -f "$ROOT/stop.sh" ]; then
  "$ROOT/stop.sh" 2>/dev/null || true
fi
pkill -f "uvicorn app.main" 2>/dev/null || true
pkill -f "react-scripts" 2>/dev/null || true
sleep 1

echo "=== Stopping Docker containers ==="
docker stop $(docker ps -q) 2>/dev/null || true
docker compose down 2>/dev/null || true

echo "=== Removing unused Docker resources ==="
docker container prune -f
docker image prune -f
docker volume prune -f
docker network prune -f
docker system prune -f

echo "=== Removing project artifacts ==="
rm -rf "$ROOT/venv"
rm -rf "$ROOT/frontend/node_modules"
rm -rf "$ROOT/backend/.pytest_cache"
find "$ROOT" -type d -name "__pycache__" -print0 2>/dev/null | xargs -0 rm -rf 2>/dev/null || true
find "$ROOT" -name "*.pyc" -delete 2>/dev/null || true
find "$ROOT" -type d -name ".pytest_cache" -print0 2>/dev/null | xargs -0 rm -rf 2>/dev/null || true
rm -f "$ROOT"/*.db 2>/dev/null || true
rm -f "$ROOT/backend"/*.db 2>/dev/null || true
rm -f "$ROOT/.backend.pid" "$ROOT/.frontend.pid" 2>/dev/null || true

# Remove Istio files if present
find "$ROOT" -path "*istio*" -type f 2>/dev/null | xargs rm -f 2>/dev/null || true
find "$ROOT" -path "*istio*" -type d -empty 2>/dev/null | xargs rmdir 2>/dev/null || true

echo "=== Cleanup complete ==="
