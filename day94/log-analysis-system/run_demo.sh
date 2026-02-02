#!/bin/bash
# Run demo: send sample logs to populate dashboard metrics (non-zero values)
set -e
API_URL="${API_URL:-http://localhost:8000}"

echo "Running demo - sending sample logs to $API_URL"
echo "This will populate patterns, trends, and may trigger anomalies/alerts."
echo ""

for i in $(seq 1 30); do
  msg="User $(shuf -i 10000-99999 -n 1) logged in from IP 192.168.1.$((RANDOM % 255))"
  rt=$((30 + RANDOM % 100))
  er=$((RANDOM % 5))
  curl -s -X POST "$API_URL/api/logs/analyze" \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"$msg\", \"level\": \"INFO\", \"source\": \"demo\", \"metrics\": {\"response_time\": $rt, \"error_rate\": $er}}" > /dev/null
  echo "  Sent log $i/30"
done

echo ""
# Validate dashboard APIs return non-zero data
PATTERNS=$(curl -s "$API_URL/api/patterns?hours=24")
TRENDS=$(curl -s "$API_URL/api/trends?hours=24")
if echo "$PATTERNS" | grep -q '"id"'; then
  echo "✅ Patterns: non-zero (dashboard will show data)"
else
  echo "⚠ Patterns: empty (run Simulator in dashboard or re-run demo)"
fi
if echo "$TRENDS" | grep -q '"metric_name"'; then
  echo "✅ Trends: non-zero (dashboard will show data)"
else
  echo "⚠ Trends: empty (run Simulator in dashboard or re-run demo)"
fi
echo ""
echo "Demo complete. Open dashboard at http://localhost:3001 and run Simulator for more data."
