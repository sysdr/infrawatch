#!/bin/bash
# Cleanup script: stop containers, remove unused Docker resources, and clean project artifacts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🧹 Cleanup: Stopping services and Docker..."

# Stop application services (backend, frontend)
if [ -f "$SCRIPT_DIR/metrics-storage-system/stop.sh" ]; then
  "$SCRIPT_DIR/metrics-storage-system/stop.sh" 2>/dev/null || true
fi
pkill -f "uvicorn app.main" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true
pkill -f "node.*metrics-storage" 2>/dev/null || true
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 3000/tcp 2>/dev/null || true
echo "✅ Application services stopped"

# Stop all Docker containers
if command -v docker &>/dev/null; then
  echo "🐳 Stopping Docker containers..."
  docker ps -aq 2>/dev/null | xargs -r docker stop 2>/dev/null || true
  echo "   Containers stopped"

  # Remove stopped containers
  docker container prune -f 2>/dev/null || true

  # Remove unused images
  docker image prune -af 2>/dev/null || true

  # Remove unused volumes
  docker volume prune -f 2>/dev/null || true

  # Remove unused networks
  docker network prune -f 2>/dev/null || true

  # Full system prune (optional - removes all unused data)
  docker system prune -af 2>/dev/null || true
  echo "✅ Docker cleanup complete"
else
  echo "⚠️  Docker not found, skipping Docker cleanup"
fi

echo ""
echo "🎉 Cleanup complete"
