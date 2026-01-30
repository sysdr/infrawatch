#!/bin/bash
# Start only the dashboard (frontend) via Docker - use this if local npm gives
# "react-scripts: Permission denied" or ERR_CONNECTION_REFUSED.
# Dashboard: http://localhost:3000

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Starting dashboard with Docker..."
docker compose up -d frontend

echo ""
echo "Wait ~1–2 minutes for the dev server to compile, then open:"
echo "  Dashboard: http://localhost:3000"
echo ""
echo "To view logs: docker compose logs -f frontend"
