#!/bin/bash
# Full cleanup: Docker + project artifacts (node_modules, venv, .pytest_cache, .pyc, Istio)
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Running cleanup.sh (Docker)..."
./cleanup.sh

echo ""
echo "Removing project artifacts..."
rm -rf frontend/node_modules
rm -rf backend/venv
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -path "*istio*" -type f 2>/dev/null | xargs rm -f 2>/dev/null || true
find . -path "*istio*" -type d 2>/dev/null | xargs rm -rf 2>/dev/null || true

echo "Full cleanup complete. Run ./build.sh to rebuild."
