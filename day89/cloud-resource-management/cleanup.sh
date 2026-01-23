#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=============================================="
echo "Cloud Resource Management - Cleanup"
echo "=============================================="

# Stop all services
echo ""
echo "1. Stopping all services..."
pkill -f "uvicorn.*8001" 2>/dev/null || true
pkill -f "react-scripts" 2>/dev/null || true
pkill -f "uvicorn app.main:app" 2>/dev/null || true
sleep 2
echo "✓ Services stopped"

# Stop Docker containers
echo ""
echo "2. Stopping Docker containers..."
if command -v docker-compose &> /dev/null && [ -f docker-compose.yml ]; then
    docker-compose down 2>/dev/null || true
    echo "✓ Docker Compose stopped"
fi

# Stop any containers related to this project
if command -v docker &> /dev/null; then
    docker ps -a --filter "name=cloud-resource" --format "{{.ID}}" | xargs -r docker stop 2>/dev/null || true
    docker ps -a --filter "name=cloud-resource" --format "{{.ID}}" | xargs -r docker rm 2>/dev/null || true
    echo "✓ Project containers removed"
fi

# Remove unused Docker resources
echo ""
echo "3. Cleaning up Docker resources..."
if command -v docker &> /dev/null; then
    echo "  - Removing unused containers..."
    docker container prune -f 2>/dev/null || true
    
    echo "  - Removing unused images..."
    docker image prune -f 2>/dev/null || true
    
    echo "  - Removing unused volumes..."
    docker volume prune -f 2>/dev/null || true
    
    echo "  - Removing unused networks..."
    docker network prune -f 2>/dev/null || true
    
    echo "✓ Docker cleanup complete"
fi

# Remove node_modules
echo ""
echo "4. Removing node_modules..."
find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
echo "✓ node_modules removed"

# Remove venv directories
echo ""
echo "5. Removing Python virtual environments..."
find . -type d -name "venv" -exec rm -rf {} + 2>/dev/null || true
echo "✓ venv directories removed"

# Remove .pytest_cache
echo ""
echo "6. Removing .pytest_cache..."
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
echo "✓ .pytest_cache removed"

# Remove .pyc files and __pycache__ directories
echo ""
echo "7. Removing Python cache files..."
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo "✓ Python cache files removed"

# Remove Istio files
echo ""
echo "8. Removing Istio files..."
find . -type d -name "*istio*" -o -name "*Istio*" 2>/dev/null | xargs -r rm -rf 2>/dev/null || true
find . -type f -name "*istio*" -o -name "*Istio*" 2>/dev/null | xargs -r rm -f 2>/dev/null || true
echo "✓ Istio files removed"

# Remove log files
echo ""
echo "9. Removing log files..."
find . -type f -name "*.log" -not -path "./.git/*" -delete 2>/dev/null || true
rm -f /tmp/backend.log /tmp/frontend.log 2>/dev/null || true
echo "✓ Log files removed"

# Remove database files (SQLite)
echo ""
echo "10. Removing SQLite database files..."
find . -type f -name "*.db" -not -path "./.git/*" -delete 2>/dev/null || true
find . -type f -name "*.db-journal" -not -path "./.git/*" -delete 2>/dev/null || true
echo "✓ Database files removed"

# Remove build artifacts
echo ""
echo "11. Removing build artifacts..."
find . -type d -name "build" -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "dist" -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".next" -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true
echo "✓ Build artifacts removed"

# Remove OS files
echo ""
echo "12. Removing OS files..."
find . -type f -name ".DS_Store" -delete 2>/dev/null || true
find . -type f -name "Thumbs.db" -delete 2>/dev/null || true
find . -type d -name ".vscode" -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true
echo "✓ OS files removed"

echo ""
echo "=============================================="
echo "Cleanup Complete!"
echo "=============================================="
echo ""
echo "Removed:"
echo "  - All services stopped"
echo "  - Docker containers and resources"
echo "  - node_modules directories"
echo "  - Python venv directories"
echo "  - .pytest_cache directories"
echo "  - .pyc files and __pycache__ directories"
echo "  - Istio files"
echo "  - Log files"
echo "  - Database files"
echo "  - Build artifacts"
echo ""
