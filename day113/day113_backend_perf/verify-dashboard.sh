#!/bin/bash
# Verify Day 113 dashboard requirements and that it is running correctly
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'
ok()  { echo -e "${GREEN}✓${NC} $*"; }
fail() { echo -e "${RED}✗${NC} $*"; exit 1; }
warn() { echo -e "${YELLOW}!${NC} $*"; }

echo "=== Day 113 Dashboard verification ==="
echo ""

# 1. Project and frontend files
[ -d "$PROJECT_DIR/frontend/src" ] || fail "Run ../setup.sh from day113 root first."
[ -f "$PROJECT_DIR/frontend/src/App.jsx" ] || fail "Missing frontend/src/App.jsx"
[ -f "$PROJECT_DIR/frontend/src/services/api.js" ] || fail "Missing frontend/src/services/api.js"
[ -f "$PROJECT_DIR/frontend/src/hooks/usePerformance.js" ] || fail "Missing frontend/src/hooks/usePerformance.js"
ok "Dashboard source files present"

# 2. Backend API
if curl -sf --connect-timeout 3 http://localhost:8000/health >/dev/null 2>&1; then
  ok "Backend API (port 8000) is running"
else
  warn "Backend not reachable at http://localhost:8000 — run ./start.sh or ../setup.sh"
fi

# 3. Performance endpoint (data the dashboard needs)
if resp=$(curl -sf --connect-timeout 3 http://localhost:8000/api/v1/metrics/performance 2>/dev/null); then
  p50=$(echo "$resp" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('latency',{}).get('p50_ms','?'))" 2>/dev/null || echo "?")
  hit=$(echo "$resp" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('cache',{}).get('hit_rate_pct','?'))" 2>/dev/null || echo "?")
  ok "Performance API returns data (p50=${p50}ms, cache hit_rate=${hit}%)"
else
  warn "Performance API not reachable — dashboard will show 'Backend unreachable' until API is up"
fi

# 4. Frontend build (optional)
if [ -d "$PROJECT_DIR/frontend/node_modules" ]; then
  ok "Frontend dependencies installed"
else
  warn "Run: cd $PROJECT_DIR/frontend && npm install --legacy-peer-deps"
fi

# 5. Dashboard dev server (optional)
if curl -sf --connect-timeout 2 http://localhost:3000 >/dev/null 2>&1 || curl -sf --connect-timeout 2 http://127.0.0.1:3000 >/dev/null 2>&1; then
  ok "Dashboard dev server (port 3000) is running — open http://localhost:3000 in your browser"
else
  warn "Dashboard not reachable on port 3000 — run: cd $PROJECT_DIR && ./start.sh or cd frontend && npm start"
  echo "  Then open http://localhost:3000 in your browser (or the URL shown by npm start)."
fi

echo ""
echo "Summary:"
echo "  - Backend API:  http://localhost:8000  (docs: http://localhost:8000/docs)"
echo "  - Dashboard:    http://localhost:3000  (start with: ./start.sh or cd frontend && npm start)"
echo "  - Ensure REACT_APP_API_URL=http://localhost:8000 (or your API URL) so the dashboard can fetch metrics."
echo ""
