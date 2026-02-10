#!/bin/bash
# cleanup.sh - Stop all services, Docker containers, and remove unused Docker
#             resources, project build artifacts, and caches.

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "=== Stopping project services ==="
if [ -f "$ROOT/stop.sh" ]; then
  "$ROOT/stop.sh" 2>/dev/null || true
fi

echo "=== Stopping Docker containers ==="
if command -v docker &>/dev/null; then
  # Stop all running containers
  running=$(docker ps -q 2>/dev/null || true)
  if [ -n "$running" ]; then
    docker stop $running 2>/dev/null || true
  fi
  # Stop all containers (including exited)
  docker container prune -f 2>/dev/null || true
  echo "=== Removing unused Docker resources ==="
  docker system prune -af 2>/dev/null || true
  docker volume prune -f 2>/dev/null || true
  docker network prune -f 2>/dev/null || true
  echo "Docker cleanup done."
else
  echo "Docker not found, skipping Docker cleanup."
fi

echo "=== Removing project caches and build artifacts ==="
# Node
rm -rf "$ROOT/node_modules" "$ROOT/frontend/node_modules" 2>/dev/null || true
# Python
rm -rf "$ROOT/venv" "$ROOT/.venv" "$ROOT/backend/venv" 2>/dev/null || true
find "$ROOT" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find "$ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$ROOT" -name "*.pyc" -delete 2>/dev/null || true
# Istio-related files (if any in project tree)
find "$ROOT" -path "*istio*" -type f 2>/dev/null | while read -r f; do rm -f "$f"; done
find "$ROOT" -path "*istio*" -type d 2>/dev/null | sort -r | while read -r d; do [ -d "$d" ] && rm -rf "$d"; done
# PID files
rm -f "$ROOT/.backend.pid" "$ROOT/.frontend.pid" 2>/dev/null || true

echo "=== Cleanup complete ==="
