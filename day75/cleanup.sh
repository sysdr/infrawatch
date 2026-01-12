#!/bin/bash

# Cleanup script for Docker resources and containers
# This script stops containers and removes unused Docker resources

set -e

echo "=========================================="
echo "Docker Cleanup Script"
echo "=========================================="
echo ""

# Stop all running containers
echo "Stopping all running containers..."
docker stop $(docker ps -aq) 2>/dev/null || echo "No containers to stop"

# Remove all stopped containers
echo "Removing all stopped containers..."
docker rm $(docker ps -aq) 2>/dev/null || echo "No containers to remove"

# Stop docker-compose services if docker-compose.yml exists
if [ -f "docker-compose.yml" ] || [ -f "user-management-ui/docker-compose.yml" ]; then
    echo "Stopping docker-compose services..."
    if [ -f "docker-compose.yml" ]; then
        docker-compose down 2>/dev/null || docker compose down 2>/dev/null || echo "No docker-compose services running"
    fi
    if [ -f "user-management-ui/docker-compose.yml" ]; then
        cd user-management-ui
        docker-compose down 2>/dev/null || docker compose down 2>/dev/null || echo "No docker-compose services running"
        cd ..
    fi
fi

# Remove unused images
echo "Removing unused Docker images..."
docker image prune -a -f 2>/dev/null || echo "No unused images to remove"

# Remove unused volumes
echo "Removing unused Docker volumes..."
docker volume prune -f 2>/dev/null || echo "No unused volumes to remove"

# Remove unused networks
echo "Removing unused Docker networks..."
docker network prune -f 2>/dev/null || echo "No unused networks to remove"

# Remove all unused resources (images, containers, networks, volumes)
echo "Performing final cleanup of all unused resources..."
docker system prune -a -f --volumes 2>/dev/null || echo "Cleanup complete"

echo ""
echo "=========================================="
echo "Docker cleanup completed!"
echo "=========================================="
echo ""
echo "Remaining Docker resources:"
docker ps -a 2>/dev/null | head -5 || echo "No containers"
docker images 2>/dev/null | head -5 || echo "No images"
echo ""
