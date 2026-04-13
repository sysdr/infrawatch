#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

echo "[build] Root: $ROOT_DIR"

if [[ ! -d "$BACKEND_DIR" || ! -d "$FRONTEND_DIR" ]]; then
  echo "[build][error] backend/frontend directories not found."
  exit 1
fi

echo "[build] Installing backend dependencies..."
cd "$BACKEND_DIR"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "[build] Installing frontend dependencies..."
cd "$FRONTEND_DIR"
npm install

echo "[build] Running backend tests..."
cd "$BACKEND_DIR"
source .venv/bin/activate
python -m pytest tests/ -v --tb=short

echo "[build] Build complete."
