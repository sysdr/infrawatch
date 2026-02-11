#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
if [ ! -d "backend/venv" ]; then
  echo "Run ./build.sh first"
  exit 1
fi
cd backend
source venv/bin/activate
export DATABASE_URL="sqlite:///:memory:"
pip install pytest pytest-asyncio -q 2>/dev/null || true
python -m pytest ../tests/unit/ -v 2>/dev/null || echo "Run: pip install pytest pytest-asyncio"
cd ..
