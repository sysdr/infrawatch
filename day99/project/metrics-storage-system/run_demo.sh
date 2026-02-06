#!/bin/bash
# Run demo to populate metrics - dashboard will display these values
set -e
API="${1:-http://localhost:8000}"
API="${API%/}"
echo "Running demo against $API..."

for i in {1..20}; do
  cpu=$((40 + RANDOM % 40))
  mem=$((50 + RANDOM % 30))
  disk=$((20 + RANDOM % 20))
  net=$((5 + RANDOM % 15))
  ts=$(date -Iseconds 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%S")
  curl -s -X POST "${API}/metrics/store" -H "Content-Type: application/json" -d "[
    {\"measurement\":\"cpu_usage\",\"source\":\"demo-server\",\"type\":\"system\",\"value\":$cpu,\"timestamp\":\"$ts\"},
    {\"measurement\":\"memory_usage\",\"source\":\"demo-server\",\"type\":\"system\",\"value\":$mem,\"timestamp\":\"$ts\"},
    {\"measurement\":\"disk_usage\",\"source\":\"demo-server\",\"type\":\"system\",\"value\":$disk,\"timestamp\":\"$ts\"},
    {\"measurement\":\"network_io\",\"source\":\"demo-server\",\"type\":\"network\",\"value\":$net,\"timestamp\":\"$ts\"}
  ]" > /dev/null
  echo "Stored batch $i (cpu=$cpu, mem=$mem, disk=$disk)"
  sleep 0.5
done
echo "Demo complete. Dashboard should now show non-zero metrics."
