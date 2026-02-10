#!/bin/bash
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT/backend"
export DATABASE_URL="sqlite:///./test.db"
PYTHON="${ROOT}/venv/bin/python3"
[ -x "$PYTHON" ] || PYTHON="python3"
"$PYTHON" -m pytest tests/ -v
