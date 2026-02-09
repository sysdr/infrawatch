#!/bin/bash
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT/backend"
export DATABASE_URL="sqlite:///./test.db"
python3 -m pytest tests/ -v
