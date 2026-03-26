#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[cleanup] stopping app processes..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "react-scripts/scripts/start.js|react-scripts start|npm start" 2>/dev/null || true

echo "[cleanup] stopping docker compose stacks..."
docker compose -f "$ROOT/docker-compose.yml" down 2>/dev/null || true
docker compose -f "$ROOT/project/docker-compose.yml" down 2>/dev/null || true

echo "[cleanup] stopping containers and pruning unused Docker resources..."
docker ps -q | xargs -r docker stop >/dev/null 2>&1 || true
docker container prune -f >/dev/null 2>&1 || true
docker image prune -f >/dev/null 2>&1 || true
docker volume prune -f >/dev/null 2>&1 || true
docker network prune -f >/dev/null 2>&1 || true

echo "[cleanup] done."
