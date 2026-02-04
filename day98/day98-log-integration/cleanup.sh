#!/bin/bash
# Cleanup script: Stop containers and remove unused Docker resources, containers, and images
# Also removes project artifacts (node_modules, venv, .pytest_cache, .pyc, Istio files)

set -e

echo "🧹 Cleanup: Day 98 Log Management Integration"
echo "=============================================="

# 1. Stop application services
echo ""
echo "🛑 Stopping application services..."
if [ -f "$(dirname "$0")/stop.sh" ]; then
    "$(dirname "$0")/stop.sh" 2>/dev/null || true
fi

# 2. Stop Docker Compose (try both commands for compatibility)
echo ""
echo "🐳 Stopping Docker Compose..."
docker compose down 2>/dev/null || docker-compose down 2>/dev/null || true

# 3. Stop all running containers
echo ""
echo "🐳 Stopping all Docker containers..."
if [ -n "$(docker ps -aq 2>/dev/null)" ]; then
    docker stop $(docker ps -aq) 2>/dev/null || true
fi

# 4. Remove Docker containers
echo ""
echo "🗑️  Removing Docker containers..."
docker container prune -f 2>/dev/null || true

# 5. Remove Docker networks
echo "🗑️  Removing Docker networks..."
docker network prune -f 2>/dev/null || true

# 6. Remove unused Docker images
echo "🗑️  Removing unused Docker images..."
docker image prune -a -f 2>/dev/null || true

# 7. Remove Docker volumes
echo "🗑️  Removing Docker volumes..."
docker volume prune -f 2>/dev/null || true

# 8. Remove Docker build cache
echo "🗑️  Removing Docker build cache..."
docker builder prune -f 2>/dev/null || true

# 9. Remove project artifacts
echo ""
echo "📁 Removing node_modules..."
rm -rf frontend/node_modules node_modules backend/node_modules 2>/dev/null || true

echo "📁 Removing venv..."
rm -rf backend/venv .venv venv env 2>/dev/null || true

echo "📁 Removing .pytest_cache..."
find . -path ./.git -prune -o -type d -name ".pytest_cache" -print0 2>/dev/null | xargs -0 -r rm -rf 2>/dev/null || true

echo "📁 Removing __pycache__ and .pyc files..."
find . -path ./.git -prune -o -type d -name "__pycache__" -print0 2>/dev/null | xargs -0 -r rm -rf 2>/dev/null || true
find . -path ./.git -prune -o -name "*.pyc" -type f -delete 2>/dev/null || true

echo "📁 Removing Istio-related files..."
find . -path ./.git -prune -o -iname "*istio*" -print0 2>/dev/null | xargs -0 -r rm -rf 2>/dev/null || true

# 10. Remove PID and log files
echo ""
echo "📁 Removing PID and temp files..."
rm -f backend.pid frontend.pid frontend.log 2>/dev/null || true

echo ""
echo "✅ Cleanup complete!"
