#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PLATFORM_DIR="${SCRIPT_DIR}"
FRONTEND_DIR="${PLATFORM_DIR}/frontend"

if [[ ! -d "$FRONTEND_DIR" ]]; then
  echo "Error: frontend not found at $FRONTEND_DIR"
  exit 1
fi

echo "=== Building frontend ==="
if [[ ! -f "${FRONTEND_DIR}/package.json" ]]; then
  echo "Error: frontend/package.json not found"
  exit 1
fi
if [[ ! -d "${FRONTEND_DIR}/node_modules" ]]; then
  echo "Installing frontend dependencies first..."
  (cd "$FRONTEND_DIR" && npm install)
fi
(cd "$FRONTEND_DIR" && npx --yes react-scripts build)
echo "Frontend build complete: ${FRONTEND_DIR}/build"

echo "=== Build complete ==="
