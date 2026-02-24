#!/usr/bin/env bash
# Stop containers and remove unused Docker resources, containers, and images.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.yml"

echo "=== Stopping project containers ==="
if [[ -f "$COMPOSE_FILE" ]]; then
  docker compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || \
  docker-compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true
fi

echo "=== Stopping all running containers ==="
docker stop $(docker ps -q) 2>/dev/null || true

echo "=== Removing stopped containers ==="
docker container prune -f

echo "=== Removing unused images (dangling) ==="
docker image prune -f

echo "=== Removing unused networks ==="
docker network prune -f

echo "=== Removing unused volumes (optional, uncomment to use) ==="
# docker volume prune -f

echo "=== Docker cleanup complete ==="
