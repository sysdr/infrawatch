#!/bin/bash
# cleanup.sh - Stop containers and remove unused Docker resources, containers, and images.
# Also stops local project services.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================"
echo "Cleanup: Stopping services and Docker"
echo "======================================"

# Stop local project services (backend, frontend)
if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null || true
    rm -f backend.pid
fi
if [ -f frontend.pid ]; then
    kill $(cat frontend.pid) 2>/dev/null || true
    rm -f frontend.pid
fi
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true
echo "✓ Local services stopped"

# Docker cleanup (no-op if Docker is not available)
if command -v docker &>/dev/null; then
    echo "Stopping Docker containers..."
    docker compose down 2>/dev/null || docker-compose down 2>/dev/null || true
    docker ps -q | xargs -r docker stop 2>/dev/null || true
    echo "Removing stopped containers..."
    docker container prune -f
    echo "Removing unused images (dangling)..."
    docker image prune -f
    echo "Removing unused images (all unused)..."
    docker image prune -a -f 2>/dev/null || true
    echo "Removing unused volumes..."
    docker volume prune -f
    echo "Removing unused networks..."
    docker network prune -f
    echo "Removing build cache..."
    docker builder prune -f 2>/dev/null || true
    echo "✓ Docker cleanup complete"
else
    echo "Docker not found or not in PATH; skipping Docker cleanup."
fi

echo ""
echo "✓ Cleanup finished"
