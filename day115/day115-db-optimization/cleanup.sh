#!/usr/bin/env bash
# Stop all containers and remove unused Docker resources, containers, and images.
# Also optionally removes project caches (node_modules, venv, .pytest_cache, .pyc).
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Stopping application services ==="
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true
pkill -f "python3 -m http.server" 2>/dev/null || true
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 3000/tcp 2>/dev/null || true
echo "App services stopped."

echo ""
echo "=== Stopping Docker Compose (this project) ==="
docker compose down -v 2>/dev/null || true
echo "Docker Compose stopped."

echo ""
echo "=== Stopping all running containers ==="
docker stop $(docker ps -q) 2>/dev/null || true
echo "Containers stopped."

echo ""
echo "=== Removing unused Docker resources ==="
docker system prune -af --volumes 2>/dev/null || true
echo "Unused images, containers, volumes, and networks removed."

echo ""
echo "=== Removing project caches and generated artifacts ==="
rm -rf frontend/node_modules 2>/dev/null || true
rm -rf backend/venv 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
# Istio-related files (if any)
find . -type d -name "istio*" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.yaml" -path "*istio*" -delete 2>/dev/null || true
echo "Caches removed (node_modules, venv, .pytest_cache, __pycache__, .pyc, Istio)."

echo ""
echo "Cleanup complete."
