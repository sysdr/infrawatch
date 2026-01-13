#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "Docker Cleanup Script"
echo "========================================"

# Stop all running containers
echo "Stopping all running containers..."
docker stop $(docker ps -q) 2>/dev/null || echo "No running containers to stop"

# Remove all stopped containers
echo "Removing stopped containers..."
docker rm $(docker ps -a -q) 2>/dev/null || echo "No containers to remove"

# Remove unused images
echo "Removing unused Docker images..."
docker image prune -a -f 2>/dev/null || echo "No unused images to remove"

# Remove unused volumes
echo "Removing unused Docker volumes..."
docker volume prune -f 2>/dev/null || echo "No unused volumes to remove"

# Remove unused networks
echo "Removing unused Docker networks..."
docker network prune -f 2>/dev/null || echo "No unused networks to remove"

# Remove build cache
echo "Removing Docker build cache..."
docker builder prune -a -f 2>/dev/null || echo "No build cache to remove"

# Remove specific project containers if they exist
echo "Removing project-specific containers..."
docker rm -f user-mgmt-postgres user-mgmt-redis 2>/dev/null || echo "Project containers not found"

# Remove project-specific volumes if they exist
echo "Removing project-specific volumes..."
docker volume rm day77-user-management-integration_postgres_data 2>/dev/null || echo "Project volumes not found"

echo ""
echo "========================================"
echo "✓ Docker Cleanup Complete!"
echo "========================================"
echo ""
echo "Summary:"
docker system df 2>/dev/null || echo "Docker system info unavailable"
echo "========================================"
