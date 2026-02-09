#!/bin/bash
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API="${1:-http://localhost:8000}"
r=$(curl -s "$API/api/dashboard" 2>/dev/null)
ex=$(echo "$r" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('executions',0))" 2>/dev/null || echo 0)
if [ "${ex:-0}" -gt 0 ] 2>/dev/null; then
  echo "Validation PASS: executions=$ex - Dashboard shows non-zero metrics"
  exit 0
else
  echo "No executions. Run: $ROOT/run_demo.sh $API"
  exit 1
fi
