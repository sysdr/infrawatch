#!/bin/bash

# Cleanup script to stop containers and remove unused Docker resources

set +e  # Continue on errors since some cleanup steps may fail if resources don't exist

echo "========================================="
echo "Docker Cleanup Script"
echo "========================================="

# Stop all running containers
echo "Stopping all running containers..."
docker-compose down 2>/dev/null || true
docker ps -aq | xargs -r docker stop 2>/dev/null || true

# Remove all stopped containers
echo "Removing stopped containers..."
docker ps -aq | xargs -r docker rm 2>/dev/null || true

# Remove unused images
echo "Removing unused images..."
docker image prune -a -f 2>/dev/null || true

# Remove unused volumes
echo "Removing unused volumes..."
docker volume prune -f 2>/dev/null || true

# Remove unused networks
echo "Removing unused networks..."
docker network prune -f 2>/dev/null || true

# System prune (removes all unused containers, networks, images, and optionally volumes)
echo "Performing system prune..."
docker system prune -a -f --volumes 2>/dev/null || true

echo "========================================="
echo "Cleanup completed!"
echo "========================================="
