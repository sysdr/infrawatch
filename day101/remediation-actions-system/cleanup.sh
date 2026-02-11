#!/bin/bash
# Cleanup script: Stop containers, remove unused Docker resources, and project artifacts
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "Cleaning up services and resources"
echo "========================================="

# Stop app services
echo "Stopping application services..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
pkill -f "node.*vite" 2>/dev/null || true
sleep 2

# Stop Docker Compose
echo "Stopping Docker Compose..."
docker compose down 2>/dev/null || true
docker-compose down 2>/dev/null || true

# Stop all running containers
echo "Stopping all Docker containers..."
docker stop $(docker ps -q) 2>/dev/null || true

# Remove stopped containers
echo "Removing stopped containers..."
docker container prune -f

# Remove unused images
echo "Removing unused images..."
docker image prune -f

# Remove unused volumes
echo "Removing unused volumes..."
docker volume prune -f

# Remove unused networks
echo "Removing unused networks..."
docker network prune -f

# Full system prune (optional - removes all unused data)
echo "Running docker system prune..."
docker system prune -f

# Remove project artifacts (optional - uncomment to use)
# echo "Removing node_modules..."
# rm -rf frontend/node_modules
# echo "Removing venv..."
# rm -rf backend/venv
# echo "Removing .pytest_cache..."
# find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
# echo "Removing __pycache__ and .pyc..."
# find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
# find . -type f -name "*.pyc" -delete 2>/dev/null || true
# echo "Removing Istio files..."
# find . -path "*istio*" -type f -delete 2>/dev/null || true
# find . -path "*istio*" -type d -exec rm -rf {} + 2>/dev/null || true

echo ""
echo "========================================="
echo "Cleanup complete"
echo "========================================="
