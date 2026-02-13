#!/bin/bash
# Verify dashboard: API returns non-zero metrics and no duplicate services
set -e
echo "=== Checking for duplicate services ==="
p8000=$(lsof -ti:8000 2>/dev/null | wc -l)
p3000=$(lsof -ti:3000 2>/dev/null | wc -l)
echo "Processes on port 8000: $p8000 (expected 1)"
echo "Processes on port 3000: $p3000 (expected 0 or 1)"
if [ "$p8000" -gt 1 ]; then
  echo "WARNING: Multiple backend processes. Run ./stop.sh then ./start.sh"
fi

echo ""
echo "=== Verifying API and non-zero metrics ==="
if ! curl -sf http://127.0.0.1:8000/api/health >/dev/null; then
  echo "Backend not running. Start with: ./start.sh"
  exit 1
fi

kpis=$(curl -s http://127.0.0.1:8000/api/kpis)
zeros=$(echo "$kpis" | python3 -c "
import json,sys
d=json.load(sys.stdin)
kpis=d.get('kpis',[])
zeros=[k for k in kpis if k.get('current_value') in (None, 0)]
if zeros:
    print('Metrics with zero/None:', [k['metric_name'] for k in zeros])
else:
    print('OK')
" 2>/dev/null)
echo "$zeros"
echo ""
echo "Sample KPI values:"
echo "$kpis" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for k in d.get('kpis',[])[:3]:
    print('  ', k['display_name'], '=', k.get('current_value'))
" 2>/dev/null
echo ""
echo "Dashboard: http://localhost:3000 (start frontend with: cd frontend && npm run dev)"
echo "API docs:  http://localhost:8000/docs"
