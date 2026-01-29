#!/bin/bash
# Stop containers and remove unused Docker resources (containers, images, volumes, networks).
# Run from project root.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "Stopping services and cleaning Docker"
echo "========================================="

# Stop project services (backend/frontend PIDs)
if [ -f "backend.pid" ]; then
    kill $(cat backend.pid) 2>/dev/null || true
    rm -f backend.pid
fi
if [ -f "frontend.pid" ]; then
    kill $(cat frontend.pid) 2>/dev/null || true
    rm -f frontend.pid
fi

# Stop and remove compose containers, networks (optionally volumes)
docker compose down 2>/dev/null || true

# Stop all running containers
docker stop $(docker ps -aq) 2>/dev/null || true

# Remove stopped containers
docker container prune -f

# Remove unused images (dangling and optionally unused)
docker image prune -af

# Remove unused volumes
docker volume prune -f

# Remove unused networks
docker network prune -f

# Optional: remove build cache (uncomment to use)
# docker builder prune -af

echo "========================================="
echo "Cleanup complete."
echo "========================================="
