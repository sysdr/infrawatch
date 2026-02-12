#!/bin/bash
cd "$(dirname "$0")"
API="${API_BASE_URL:-http://localhost:8000/api/v1}"
echo "Running demo against $API ..."
# Create a demo workflow
WORKFLOW_JSON=$(curl -s -X POST "$API/workflows/" -H "Content-Type: application/json" -d '{"name":"Demo Workflow","description":"Sample workflow for dashboard demo","definition":{"steps":[{"name":"step1","type":"script","script":"echo hello"},{"name":"step2","type":"api"},{"name":"step3","type":"transform"}]}}')
WORKFLOW_ID=$(echo "$WORKFLOW_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null)
if [ -z "$WORKFLOW_ID" ]; then
  echo "Failed to create workflow. Is backend running?"
  exit 1
fi
echo "Created workflow ID: $WORKFLOW_ID"
# Run 2 executions so dashboard has data
for i in 1 2; do
  curl -s -X POST "$API/executions/" -H "Content-Type: application/json" -d "{\"workflow_id\":$WORKFLOW_ID,\"input_data\":{\"run\":$i}}" > /dev/null
  echo "Started execution $i"
done
echo "Demo complete. Wait a few seconds then refresh the dashboard."
