#!/bin/bash

# Cleanup script for Infrastructure Discovery System
# This script stops all containers and removes unused Docker resources

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo "Infrastructure Discovery - Cleanup Script"
echo "=========================================="
echo ""

# Stop all services
echo "1. Stopping all services..."
cd "$PROJECT_ROOT"
if [ -f "scripts/stop.sh" ]; then
    ./scripts/stop.sh 2>/dev/null || true
fi

# Kill any remaining processes
echo "2. Killing remaining processes..."
pkill -f "react-scripts start" 2>/dev/null || true
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "node.*react-scripts" 2>/dev/null || true
sleep 2

# Stop Docker containers
echo "3. Stopping Docker containers..."
cd "$PROJECT_ROOT/docker" 2>/dev/null || cd "$PROJECT_ROOT"
if [ -f "docker/docker-compose.yml" ]; then
    docker-compose -f docker/docker-compose.yml down -v 2>/dev/null || true
fi

# Remove project-specific containers
echo "4. Removing project containers..."
docker ps -a --filter "name=infrastructure-discovery" --filter "name=discovery" --filter "name=docker-postgres" --filter "name=docker-redis" --format "{{.ID}}" | xargs -r docker rm -f 2>/dev/null || true

# Remove unused Docker resources
echo "5. Cleaning up unused Docker resources..."

# Remove stopped containers
docker container prune -f 2>/dev/null || true

# Remove unused networks
docker network prune -f 2>/dev/null || true

# Remove unused images (optional - commented out to avoid removing base images)
# docker image prune -f 2>/dev/null || true

# Remove unused volumes (be careful with this)
echo "6. Removing unused volumes..."
docker volume prune -f 2>/dev/null || true

# Remove build cache (optional)
echo "7. Cleaning build cache..."
docker builder prune -f 2>/dev/null || true

# Show remaining Docker resources
echo ""
echo "=========================================="
echo "Docker Resources Summary:"
echo "=========================================="
echo "Containers:"
docker ps -a --filter "name=infrastructure-discovery" --filter "name=discovery" --filter "name=docker-postgres" --filter "name=docker-redis" 2>/dev/null || echo "  No project containers found"
echo ""
echo "Volumes:"
docker volume ls --filter "name=infrastructure-discovery" --filter "name=discovery" --filter "name=postgres_data" 2>/dev/null || echo "  No project volumes found"
echo ""
echo "Networks:"
docker network ls --filter "name=infrastructure-discovery" --filter "name=discovery" --filter "name=docker_default" 2>/dev/null || echo "  No project networks found"
echo ""

echo "=========================================="
echo "Cleanup complete!"
echo "=========================================="
