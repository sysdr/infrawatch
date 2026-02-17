#!/usr/bin/env bash
# cleanup.sh - Stop containers and remove unused Docker resources, containers, and images.
# Run from project root: ./cleanup.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Stopping Docker Compose services ==="
if command -v docker &>/dev/null; then
  if [ -f docker/docker-compose.yml ]; then
    (cd docker && docker compose down 2>/dev/null) || (cd docker && docker-compose down 2>/dev/null) || true
  fi
  echo "=== Stopping all running containers ==="
  docker stop $(docker ps -q) 2>/dev/null || true
  echo "=== Removing unused Docker resources ==="
  docker system prune -af --volumes 2>/dev/null || true
  docker container prune -f 2>/dev/null || true
  docker image prune -af 2>/dev/null || true
  docker volume prune -f 2>/dev/null || true
  docker network prune -f 2>/dev/null || true
  echo "Docker cleanup done."
else
  echo "Docker not found or not in PATH. Skipping Docker cleanup."
fi

echo "=== Removing project artifacts ==="
rm -rf backend/venv
rm -rf frontend/node_modules
rm -rf tests/.pytest_cache
find . -depth -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
# Istio-generated or local k8s/istio manifests (if any)
find . -type f \( -name "*-istio*.yaml" -o -name "*-istio*.yml" \) -delete 2>/dev/null || true

echo "Cleanup complete."
