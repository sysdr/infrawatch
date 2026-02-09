#!/bin/bash
set -e
API="${1:-http://localhost:8000}"
API="${API%/}"
echo "Running demo against $API..."

# Create demo jobs (skip if already exist)
for i in 1 2 3 4 5; do
  curl -s -X POST "${API}/api/jobs" -H "Content-Type: application/json" -d "{\"name\":\"demo-job-$i\",\"command\":\"echo demo-$i\"}" > /dev/null || true
done

# Trigger executions
JOBS=$(curl -s "${API}/api/jobs" | python3 -c "import sys,json; jobs=json.load(sys.stdin); print(' '.join(j['id'] for j in jobs[:5]))" 2>/dev/null || echo "")
for jid in $JOBS; do
  curl -s -X POST "${API}/api/jobs/$jid/trigger" > /dev/null
  echo "Triggered job $jid"
done

echo "Demo complete. Dashboard should show non-zero metrics."
