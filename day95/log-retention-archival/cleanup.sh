#!/bin/bash
# Stop all containers and remove unused Docker resources (containers, images, networks, volumes).
# Optionally remove project artifacts: node_modules, venv, .pytest_cache, __pycache__, .pyc, Istio.

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Stopping Docker Compose services ==="
docker compose down --remove-orphans 2>/dev/null || true

echo "=== Stopping any remaining containers ==="
docker stop $(docker ps -q) 2>/dev/null || true

echo "=== Removing unused Docker resources ==="
docker container prune -f
docker image prune -f
docker network prune -f
docker volume prune -f
docker system prune -f

echo "=== Removing project artifacts ==="
rm -rf frontend/node_modules backend/node_modules node_modules
rm -rf backend/venv venv .venv
rm -rf .pytest_cache backend/.pytest_cache tests/.pytest_cache
find backend tests -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find backend tests -name "*.pyc" -delete 2>/dev/null || true
find . -maxdepth 3 -type d -name "istio" -exec rm -rf {} + 2>/dev/null || true

echo "=== Cleanup complete ==="
