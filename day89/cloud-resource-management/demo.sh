#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
API="${REACT_APP_API_URL:-http://localhost:8001}"

echo "=============================================="
echo "Cloud Resource Management - Demo"
echo "=============================================="

wait_for_backend() {
  for i in $(seq 1 30); do
    if curl -sf "$API/" > /dev/null 2>&1; then return 0; fi
    sleep 1
  done
  echo "Backend not ready. Start with ./start.sh first."
  exit 1
}

wait_for_backend

echo "1. Provisioning demo resources..."
curl -sf -X POST "$API/api/resources/provision" -H "Content-Type: application/json" \
  -d '{"name": "demo-compute-1", "type": "compute", "provider": "aws", "region": "us-east-1", "team": "engineering", "size": 2}' > /dev/null 2>&1 || true
curl -sf -X POST "$API/api/resources/provision" -H "Content-Type: application/json" \
  -d '{"name": "demo-compute-2", "type": "compute", "provider": "aws", "region": "us-east-1", "team": "engineering", "size": 1}' > /dev/null 2>&1 || true
curl -sf -X POST "$API/api/resources/provision" -H "Content-Type: application/json" \
  -d '{"name": "demo-storage-1", "type": "storage", "provider": "aws", "region": "us-east-1", "team": "engineering", "size": 1}' > /dev/null 2>&1 || true
curl -sf -X POST "$API/api/resources/provision" -H "Content-Type: application/json" \
  -d '{"name": "demo-db-1", "type": "database", "provider": "aws", "region": "us-east-1", "team": "engineering", "size": 1}' > /dev/null 2>&1 || true

echo "   Waiting for provisioning (simulated)..."
sleep 4

echo "2. Running compliance check..."
curl -sf -X POST "$API/api/compliance/check-all" > /dev/null 2>&1 || true

echo "3. Auto-tagging resources..."
curl -sf -X POST "$API/api/tags/auto-tag" > /dev/null 2>&1 || true

echo "4. Fetching cost optimizations (triggers analysis)..."
curl -sf "$API/api/cost/optimizations" > /dev/null 2>&1 || true

echo "5. Dashboard stats:"
curl -s "$API/api/stats/dashboard" | python3 -c "
import sys, json
d = json.load(sys.stdin)
r = d.get('resources', {})
c = d.get('costs', {})
print('   Resources:', r.get('total', 0), 'total,', r.get('active', 0), 'active')
print('   Monthly cost: \$' + str(c.get('total_monthly', 0)))
print('   Potential savings: \$' + str(c.get('potential_savings', 0)))
" 2>/dev/null || echo "   (could not parse)"

echo ""
echo "Demo complete. Refresh the dashboard at http://localhost:3000"
