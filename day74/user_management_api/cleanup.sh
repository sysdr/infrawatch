#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Docker Cleanup Script ==="
echo ""

# Stop any running containers from docker-compose
echo "Stopping docker-compose services..."
docker-compose down 2>/dev/null || true

# Stop all containers related to this project
echo "Stopping project containers..."
docker ps -a --filter "name=user" --filter "name=postgres" --filter "name=redis" --format "{{.ID}}" | xargs -r docker stop 2>/dev/null || true

# Remove stopped containers
echo "Removing stopped containers..."
docker ps -a --filter "name=user" --filter "name=postgres" --filter "name=redis" --format "{{.ID}}" | xargs -r docker rm 2>/dev/null || true

# Remove unused Docker images
echo "Removing unused Docker images..."
docker image prune -f 2>/dev/null || true

# Remove unused Docker volumes
echo "Removing unused Docker volumes..."
docker volume prune -f 2>/dev/null || true

# Remove unused Docker networks
echo "Removing unused Docker networks..."
docker network prune -f 2>/dev/null || true

# Remove all unused Docker resources (containers, networks, images, build cache)
echo "Performing full Docker system cleanup..."
docker system prune -af --volumes 2>/dev/null || true

echo ""
echo "=== Cleanup Complete ==="
echo ""
echo "Removed:"
echo "  - Stopped containers"
echo "  - Unused images"
echo "  - Unused volumes"
echo "  - Unused networks"
echo "  - Build cache"
echo ""
echo "Note: This script removes ALL unused Docker resources system-wide."
echo "      Use with caution in shared Docker environments."
