#!/bin/bash
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT/backend"
echo "Running backend tests..."
python3 -m pytest tests/ -v
echo ""
echo "To validate dashboard metrics (backend must be running):"
echo "  1. $ROOT/start.sh   # or start backend manually"
echo "  2. $ROOT/run_demo.sh http://localhost:8000"
echo "  3. $ROOT/validate.sh http://localhost:8000"
