#!/bin/bash
# cleanup.sh - Stop containers and remove unused Docker resources, containers, and images
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "=== Docker & Service Cleanup ==="

# Stop project services (backend, frontend)
if [ -f "$ROOT/metrics-storage-system/stop.sh" ]; then
  echo "Stopping project services..."
  "$ROOT/metrics-storage-system/stop.sh" 2>/dev/null || true
fi

# Stop all Docker containers
echo "Stopping Docker containers..."
docker stop $(docker ps -q) 2>/dev/null || true

# Remove stopped containers
echo "Removing stopped containers..."
docker container prune -f

# Remove unused images (dangling)
echo "Removing dangling images..."
docker image prune -f

# Remove unused images (all without containers)
echo "Removing unused images..."
docker image prune -a -f

# Remove unused volumes
echo "Removing unused volumes..."
docker volume prune -f

# Remove unused networks
echo "Removing unused networks..."
docker network prune -f

# Remove build cache
echo "Removing build cache..."
docker builder prune -f 2>/dev/null || true

echo ""
echo "✅ Docker cleanup complete."
