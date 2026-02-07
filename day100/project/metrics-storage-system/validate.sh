#!/bin/bash
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API="${1:-http://localhost:8000}"
echo "Validating metrics at $API..."
r=$(curl -s "$API/api/metrics" 2>/dev/null)
total=$(echo "$r" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('summary',{}).get('total',0))" 2>/dev/null || echo 0)
cpu=$(echo "$r" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('summary',{}).get('cpu_avg',0))" 2>/dev/null || echo 0)
if [ "$total" -gt 0 ] 2>/dev/null; then
  echo "✅ Validation PASS: Total=$total, CPU avg=$cpu% - Dashboard will show non-zero metrics"
  exit 0
else
  echo "⚠️  Validation: No metrics yet. Run: $ROOT/run_demo.sh $API"
  exit 1
fi
