#!/bin/bash

set -e

echo "=========================================="
echo "Day 76: Cleanup Script"
echo "=========================================="

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "1. Stopping Docker containers..."
if [ -f "docker-compose.yml" ]; then
    docker-compose down -v 2>/dev/null || true
    echo "   ✓ Docker containers stopped and removed"
else
    echo "   ⚠ docker-compose.yml not found, skipping"
fi

echo ""
echo "2. Removing Docker resources..."
# Remove containers
docker ps -a --filter "name=day76" --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null || true

# Remove images
docker images --filter "reference=day76*" --format "{{.ID}}" | xargs -r docker rmi -f 2>/dev/null || true

# Remove volumes
docker volume ls --filter "name=day76" --format "{{.Name}}" | xargs -r docker volume rm 2>/dev/null || true

# Remove networks
docker network ls --filter "name=day76" --format "{{.ID}}" | xargs -r docker network rm 2>/dev/null || true

echo "   ✓ Docker resources cleaned up"

echo ""
echo "3. Removing Python virtual environments..."
find . -type d -name "venv" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".venv" -exec rm -rf {} + 2>/dev/null || true
echo "   ✓ Virtual environments removed"

echo ""
echo "4. Removing node_modules..."
find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
echo "   ✓ node_modules removed"

echo ""
echo "5. Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.pyd" -delete 2>/dev/null || true
echo "   ✓ Python cache files removed"

echo ""
echo "6. Removing test cache..."
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name ".coverage" -delete 2>/dev/null || true
find . -type f -name "coverage.xml" -delete 2>/dev/null || true
find . -type f -name "htmlcov" -delete 2>/dev/null || true
find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
echo "   ✓ Test cache removed"

echo ""
echo "7. Removing IDE files..."
find . -type d -name ".idea" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".vscode" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.swp" -delete 2>/dev/null || true
find . -type f -name "*.swo" -delete 2>/dev/null || true
find . -type f -name "*~" -delete 2>/dev/null || true
echo "   ✓ IDE files removed"

echo ""
echo "8. Removing build artifacts..."
find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
echo "   ✓ Build artifacts removed"

echo ""
echo "9. Pruning unused Docker resources..."
docker system prune -f --volumes 2>/dev/null || true
echo "   ✓ Unused Docker resources pruned"

echo ""
echo "=========================================="
echo "Cleanup completed successfully!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  - Docker containers: Stopped and removed"
echo "  - Docker images: Removed"
echo "  - Docker volumes: Removed"
echo "  - Docker networks: Removed"
echo "  - Python venv: Removed"
echo "  - node_modules: Removed"
echo "  - Python cache: Removed"
echo "  - Test cache: Removed"
echo "  - Build artifacts: Removed"
echo ""
