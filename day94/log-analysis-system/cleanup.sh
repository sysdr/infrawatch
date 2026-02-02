#!/bin/bash
# cleanup.sh - Stop containers and remove unused Docker resources, containers, and images.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Stopping Docker Compose stack ==="
docker compose down 2>/dev/null || docker-compose down 2>/dev/null || true

echo "=== Stopping all running containers (project and others) ==="
containers=$(docker ps -aq 2>/dev/null) && [ -n "$containers" ] && docker stop $containers || true

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

echo "=== Removing unused build cache ==="
docker builder prune -f

echo "✅ Docker cleanup complete"
