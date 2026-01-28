#!/bin/bash
# Demo: ingest sample logs via API so dashboard shows non-zero metrics
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
API="${API_URL:-http://localhost:8000}"

echo "Demo: Ingesting sample logs to $API"
for i in $(seq 1 50); do
  curl -s -X POST "$API/api/logs/ingest" -H "Content-Type: application/json" -d "{\"timestamp\":\"$(date -Iseconds)\",\"level\":\"INFO\",\"service\":\"demo-$((i % 4 + 1))\",\"message\":\"Demo log entry $i\"}" > /dev/null
done
echo "Ingested 50 logs via API"
curl -s "$API/api/metrics/summary" | python3 -c "import sys,json; d=json.load(sys.stdin); print('Total logs:', d.get('total_logs',0)); print('Hot storage:', d.get('storage',{}).get('hot',{}).get('count',0))"
