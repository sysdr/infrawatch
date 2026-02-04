#!/bin/bash
# Serve the standalone dashboard - no Docker, no npm, no backend required

cd "$(dirname "$0")"
PORT="${1:-8080}"

echo "=========================================="
echo "  Log Dashboard - Standalone Mode"
echo "=========================================="
echo ""
echo "  Open in browser: http://localhost:$PORT/dashboard.html"
echo ""
echo "  Press Ctrl+C to stop"
echo "=========================================="
echo ""

python3 -m http.server "$PORT" 2>/dev/null || python -m http.server "$PORT"
