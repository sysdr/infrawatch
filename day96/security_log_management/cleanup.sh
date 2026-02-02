#!/bin/bash
# cleanup.sh - Stop containers, remove unused Docker resources, and clean project artifacts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Cleanup Script ==="

# Remove project artifacts (node_modules, venv, .pytest_cache, __pycache__, .pyc)
echo "Removing project artifacts..."
rm -rf backend/venv backend/.venv .venv venv 2>/dev/null || true
rm -rf backend/.pytest_cache .pytest_cache 2>/dev/null || true
rm -rf frontend/node_modules node_modules 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*istio*" -type f -delete 2>/dev/null || true
find . -name "*istio*" -type d -exec rm -rf {} + 2>/dev/null || true
echo "Project artifacts removed"

# Stop project services first (local PIDs)
if [ -f "$SCRIPT_DIR/.backend.pid" ]; then
    kill $(cat "$SCRIPT_DIR/.backend.pid") 2>/dev/null || true
    rm -f "$SCRIPT_DIR/.backend.pid"
    echo "Stopped local backend"
fi
if [ -f "$SCRIPT_DIR/.frontend.pid" ]; then
    kill $(cat "$SCRIPT_DIR/.frontend.pid") 2>/dev/null || true
    rm -f "$SCRIPT_DIR/.frontend.pid"
    echo "Stopped local frontend"
fi

# Stop Docker Compose services for this project
if [ -f "$SCRIPT_DIR/docker/docker-compose.yml" ]; then
    echo "Stopping Docker Compose services..."
    docker compose -f "$SCRIPT_DIR/docker/docker-compose.yml" down 2>/dev/null || \
    docker-compose -f "$SCRIPT_DIR/docker/docker-compose.yml" down 2>/dev/null || true
    echo "Docker Compose services stopped"
fi

# Stop all running containers
echo "Stopping all running containers..."
docker stop $(docker ps -q) 2>/dev/null || echo "No running containers"

# Remove stopped containers
echo "Removing stopped containers..."
docker container prune -f

# Remove unused images (dangling)
echo "Removing dangling images..."
docker image prune -f

# Remove unused images (all unused, not just dangling) - optional, uncomment if desired
# docker image prune -a -f

# Remove unused volumes
echo "Removing unused volumes..."
docker volume prune -f

# Remove unused networks
echo "Removing unused networks..."
docker network prune -f

# Optional: Remove all unused build cache
echo "Removing build cache..."
docker builder prune -f 2>/dev/null || true

echo "=== Cleanup complete ==="
