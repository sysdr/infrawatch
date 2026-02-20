#!/usr/bin/env bash
# cleanup.sh - Stop containers and remove unused Docker resources, containers, and images.
# Also removes project cruft: node_modules, venv, .pytest_cache, .pyc, Istio-related files.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Stopping Docker Compose ==="
docker compose -f docker/docker-compose.yml down 2>/dev/null || true

echo "=== Stopping all running containers ==="
docker stop $(docker ps -q) 2>/dev/null || true

echo "=== Removing stopped containers ==="
docker container prune -f

echo "=== Removing unused images (dangling) ==="
docker image prune -f

echo "=== Removing unused images (all unused, not just dangling) ==="
docker image prune -a -f

echo "=== Removing unused volumes ==="
docker volume prune -f

echo "=== Removing unused networks ==="
docker network prune -f

echo "=== Removing build cache ==="
docker builder prune -f

echo "=== Project cruft: node_modules, venv, .pytest_cache, .pyc, __pycache__, Istio ==="
for dir in node_modules venv .pytest_cache __pycache__; do
  find . -type d -name "$dir" -not -path "./.git/*" -print0 2>/dev/null | xargs -0 rm -rf 2>/dev/null || true
done
find . -name "*.pyc" -not -path "./.git/*" -delete 2>/dev/null || true
find . -name "*.pyo" -not -path "./.git/*" -delete 2>/dev/null || true
find . -type d -iname "*istio*" -not -path "./.git/*" -print0 2>/dev/null | xargs -0 rm -rf 2>/dev/null || true
find . -type f -iname "*istio*" -not -path "./.git/*" -delete 2>/dev/null || true

echo "=== Docker cleanup complete ==="
docker system df
