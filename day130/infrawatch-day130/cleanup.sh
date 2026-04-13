#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$ROOT_DIR"
BACKEND_PORT=8130
FRONTEND_PORT=3130

echo "[cleanup] Root: $ROOT_DIR"

echo "[cleanup] Stopping local services on ports ${BACKEND_PORT}/${FRONTEND_PORT}..."
pkill -f "uvicorn.*${BACKEND_PORT}" 2>/dev/null || true
pkill -f "vite.*${FRONTEND_PORT}" 2>/dev/null || true
rm -f /tmp/infrawatch-backend-130.pid /tmp/infrawatch-frontend-130.pid

if command -v docker >/dev/null 2>&1; then
  echo "[cleanup] Stopping docker compose stack (if present)..."
  if [[ -f "$PROJECT_DIR/docker-compose.yml" ]]; then
    if docker compose -f "$PROJECT_DIR/docker-compose.yml" config >/dev/null 2>&1; then
      docker compose -f "$PROJECT_DIR/docker-compose.yml" down -v --remove-orphans || true
    else
      echo "[cleanup] docker-compose.yml is invalid; skipping compose down."
    fi
  fi

  echo "[cleanup] Stopping matching project containers..."
  docker ps -aq --filter "name=infrawatch-push-backend" | xargs -r docker rm -f
  docker ps -aq --filter "name=infrawatch-push-frontend" | xargs -r docker rm -f

  echo "[cleanup] Pruning unused Docker resources..."
  docker container prune -f || true
  docker image prune -f || true
  docker volume prune -f || true
  docker network prune -f || true
else
  echo "[cleanup] Docker not installed, skipping docker cleanup."
fi

echo "[cleanup] Removing target directories from day130..."
export ROOT_DIR
python3 - <<'PY'
import os
from pathlib import Path
root = Path(os.environ["ROOT_DIR"])
removed = 0
for p in root.rglob("target"):
    if p.is_dir():
        for child in sorted(p.rglob("*"), reverse=True):
            if child.is_file() or child.is_symlink():
                child.unlink(missing_ok=True)
            elif child.is_dir():
                try:
                    child.rmdir()
                except OSError:
                    pass
        try:
            p.rmdir()
            removed += 1
        except OSError:
            pass
print(f"[cleanup] target directories removed: {removed}")
PY

echo "[cleanup] Done."
