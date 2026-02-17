#!/bin/bash
# Run demo (create template, report, generate) and validate dashboard stats are updated.
set -e

API="${API_BASE_URL:-http://localhost:8000/api}"
echo "Using API base: $API"

# Wait for backend
for i in $(seq 1 15); do
  if curl -sf "$API/../health" >/dev/null 2>&1; then break; fi
  echo "Waiting for backend... ($i/15)"
  sleep 2
done
curl -sf "$API/../health" || { echo "Backend not available"; exit 1; }

# Initial dashboard stats
echo "=== Initial dashboard stats ==="
curl -s "$API/dashboard/stats" | python3 -m json.tool

# Create template (unique name so script can run multiple times)
DEMO_NAME="Demo-$(date +%s)"
echo "=== Creating template: $DEMO_NAME ==="
TEMPLATE_RESP=$(curl -s -X POST "$API/templates/" -H "Content-Type: application/json" -d "{
  \"name\": \"$DEMO_NAME\",
  \"description\": \"Demo\",
  \"query_config\": {\"metrics\": [\"cpu_usage\", \"memory_usage\"], \"aggregations\": {\"cpu_usage\": \"mean\"}},
  \"layout_config\": {\"title\": \"Demo Report\", \"sections\": [{\"title\": \"Metrics\", \"type\": \"table\"}]}
}")
TEMPLATE_ID=$(echo "$TEMPLATE_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id','') if isinstance(d,dict) else '')" 2>/dev/null)
echo "Template response: $TEMPLATE_RESP"
echo "Template ID: $TEMPLATE_ID"
if [ -z "$TEMPLATE_ID" ]; then echo "Failed to create template"; exit 1; fi

# Create report
echo "=== Creating report ==="
REPORT_RESP=$(curl -s -X POST "$API/reports/" -H "Content-Type: application/json" -d "{
  \"name\": \"$DEMO_NAME-report\",
  \"template_id\": $TEMPLATE_ID,
  \"parameters\": {\"time_range\": \"7d\"},
  \"output_formats\": [\"json\", \"csv\"]
}")
REPORT_ID=$(echo "$REPORT_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id','') if isinstance(d,dict) else '')" 2>/dev/null)
echo "Report ID: $REPORT_ID"
if [ -z "$REPORT_ID" ]; then echo "Failed to create report"; exit 1; fi

# Trigger generate
echo "=== Generating report ==="
curl -s -X POST "$API/reports/$REPORT_ID/generate"

# Wait for execution to complete
echo "Waiting for report generation (15s)..."
sleep 15

# Dashboard stats after demo
echo "=== Dashboard stats after demo ==="
STATS=$(curl -s "$API/dashboard/stats")
echo "$STATS" | python3 -m json.tool

# Validate: templates, reports, executions should be >= 1; executions_completed >= 0
TEMPLATES=$(echo "$STATS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('templates',0))")
REPORTS=$(echo "$STATS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('reports',0))")
EXEC_TOTAL=$(echo "$STATS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('executions_total',0))")

echo ""
if [ "$TEMPLATES" -ge 1 ] && [ "$REPORTS" -ge 1 ] && [ "$EXEC_TOTAL" -ge 1 ]; then
  echo "✓ Dashboard validation passed: templates=$TEMPLATES, reports=$REPORTS, executions_total=$EXEC_TOTAL"
else
  echo "✗ Dashboard validation failed: templates=$TEMPLATES, reports=$REPORTS, executions_total=$EXEC_TOTAL"
  exit 1
fi
