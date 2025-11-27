#!/bin/bash

echo "=========================================="
echo "Report Templates System Demo"
echo "=========================================="

API_URL="http://localhost:8000"

echo "1. Creating template..."
TEMPLATE_ID=$(curl -s -X POST "$API_URL/api/templates" \
  -H "Content-Type: application/json" \
  -d @sample-templates/weekly_summary.json | jq -r '.id')
echo "Template created with ID: $TEMPLATE_ID"

echo "2. Creating scheduled report..."
SCHEDULE_ID=$(curl -s -X POST "$API_URL/api/reports/schedules" \
  -H "Content-Type: application/json" \
  -d "{
    \"template_id\": $TEMPLATE_ID,
    \"name\": \"Weekly Summary Report\",
    \"schedule_cron\": \"0 9 * * MON\",
    \"recipients\": [\"team@example.com\"]
  }" | jq -r '.id')
echo "Schedule created with ID: $SCHEDULE_ID"

echo "3. Generating report..."
EXECUTION_ID=$(curl -s -X POST "$API_URL/api/reports/generate" \
  -H "Content-Type: application/json" \
  -d "{
    \"scheduled_report_id\": $SCHEDULE_ID
  }" | jq -r '.execution_id')
echo "Report execution ID: $EXECUTION_ID"

echo ""
echo "Demo complete! Check:"
echo "- Frontend: http://localhost:3000"
echo "- API Docs: http://localhost:8000/docs"
