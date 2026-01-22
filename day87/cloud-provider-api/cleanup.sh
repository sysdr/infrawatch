#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================="
echo "Docker and System Cleanup Script"
echo "=================================="

# Stop all services first
echo "Stopping all services..."
if [ -f "stop.sh" ]; then
    bash stop.sh
fi

# Stop Docker containers
echo ""
echo "Stopping Docker containers..."
docker ps -aq 2>/dev/null | xargs -r docker stop 2>/dev/null || echo "No containers to stop"

# Remove Docker containers
echo "Removing Docker containers..."
docker ps -aq 2>/dev/null | xargs -r docker rm 2>/dev/null || echo "No containers to remove"

# Remove unused Docker images
echo "Removing unused Docker images..."
docker image prune -af 2>/dev/null || echo "No unused images to remove"

# Remove unused Docker volumes
echo "Removing unused Docker volumes..."
docker volume prune -f 2>/dev/null || echo "No unused volumes to remove"

# Remove unused Docker networks
echo "Removing unused Docker networks..."
docker network prune -f 2>/dev/null || echo "No unused networks to remove"

# Remove all unused Docker resources
echo "Removing all unused Docker resources..."
docker system prune -af --volumes 2>/dev/null || echo "Docker cleanup complete"

echo ""
echo "=================================="
echo "Project Cleanup"
echo "=================================="

# Remove node_modules
echo "Removing node_modules directories..."
find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null
echo "✓ node_modules removed"

# Remove Python virtual environments
echo "Removing Python virtual environments..."
find . -type d -name "venv" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".venv" -exec rm -rf {} + 2>/dev/null
find . -type d -name "env" -exec rm -rf {} + 2>/dev/null
echo "✓ Python virtual environments removed"

# Remove __pycache__ directories
echo "Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo "✓ __pycache__ directories removed"

# Remove .pyc and .pyo files
echo "Removing .pyc and .pyo files..."
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null
find . -type f -name "*.pyd" -delete 2>/dev/null
echo "✓ Python cache files removed"

# Remove .pytest_cache
echo "Removing .pytest_cache directories..."
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
echo "✓ .pytest_cache removed"

# Remove Istio files
echo "Removing Istio files..."
find . -type f -name "*istio*" -delete 2>/dev/null
find . -type f -name "*Istio*" -delete 2>/dev/null
find . -type d -name "*istio*" -exec rm -rf {} + 2>/dev/null
find . -type d -name "*Istio*" -exec rm -rf {} + 2>/dev/null
echo "✓ Istio files removed"

# Remove PID files
echo "Removing PID files..."
find . -type f -name "*.pid" -delete 2>/dev/null
find . -type f -name ".backend.pid" -delete 2>/dev/null
find . -type f -name ".frontend.pid" -delete 2>/dev/null
echo "✓ PID files removed"

# Remove log files
echo "Removing log files..."
find . -type f -name "*.log" -delete 2>/dev/null
rm -f /tmp/backend.log /tmp/frontend.log /tmp/frontend_live.log /tmp/frontend_final.log 2>/dev/null
echo "✓ Log files removed"

# Remove .DS_Store files (macOS)
echo "Removing .DS_Store files..."
find . -type f -name ".DS_Store" -delete 2>/dev/null
echo "✓ .DS_Store files removed"

# Remove coverage files
echo "Removing coverage files..."
find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null
find . -type f -name ".coverage" -delete 2>/dev/null
find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".nyc_output" -exec rm -rf {} + 2>/dev/null
echo "✓ Coverage files removed"

# Remove build artifacts
echo "Removing build artifacts..."
find . -type d -name "build" -not -path "*/node_modules/*" -exec rm -rf {} + 2>/dev/null
find . -type d -name "dist" -not -path "*/node_modules/*" -exec rm -rf {} + 2>/dev/null
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null
echo "✓ Build artifacts removed"

echo ""
echo "=================================="
echo "✓ Cleanup Complete!"
echo "=================================="
echo ""
echo "Removed:"
echo "  - Docker containers, images, volumes, and networks"
echo "  - node_modules directories"
echo "  - Python virtual environments"
echo "  - __pycache__ directories and .pyc files"
echo "  - .pytest_cache directories"
echo "  - Istio files"
echo "  - PID and log files"
echo "  - Build artifacts"
echo ""
