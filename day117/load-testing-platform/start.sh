#!/usr/bin/env bash
# Start backend. Uses full paths and avoids duplicate services.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_DIR="${SCRIPT_DIR}"
BACKEND_DIR="${PLATFORM_DIR}/backend"
VENV_BIN="${PLATFORM_DIR}/.venv/bin"
UVICORN="${VENV_BIN}/uvicorn"

if [[ ! -d "$PLATFORM_DIR" ]] || [[ ! -x "$UVICORN" ]]; then
  echo "Error: Run setup.sh first (missing platform or venv)."
  exit 1
fi

if command -v ss &>/dev/null; then
  if ss -tlnp 2>/dev/null | grep -q ':8117 '; then
    echo "Port 8117 already in use. Stop existing backend to avoid duplicate."
    ss -tlnp 2>/dev/null | grep 8117 || true
    exit 1
  fi
fi

echo "Starting backend at http://0.0.0.0:8117 (cwd=${BACKEND_DIR})"
cd "$BACKEND_DIR"
exec "$UVICORN" app.main:app --host 0.0.0.0 --port 8117
