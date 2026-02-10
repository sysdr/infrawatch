#!/bin/bash
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API="${1:-http://localhost:8000}"
r=$(curl -s "$API/api/dashboard" 2>/dev/null)
webhooks=$(echo "$r" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('webhooks_received',0))" 2>/dev/null || echo 0)
integrations=$(echo "$r" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('integrations',0))" 2>/dev/null || echo 0)
if [ "${webhooks:-0}" -gt 0 ] 2>/dev/null || [ "${integrations:-0}" -gt 0 ] 2>/dev/null; then
  echo "Validation PASS: integrations=$integrations webhooks_received=$webhooks - Dashboard shows non-zero metrics"
  exit 0
else
  echo "No data. Run: $ROOT/run_demo.sh $API"
  exit 1
fi
