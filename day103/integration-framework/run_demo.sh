#!/bin/bash
set -e
API="${1:-http://localhost:8000}"
API="${API%/}"
echo "Running demo against $API..."

# Create integrations (unique names to avoid conflicts)
for i in 1 2 3 4 5; do
  curl -s -X POST "${API}/api/integrations" -H "Content-Type: application/json" \
    -d "{\"name\":\"demo-integration-$i-$$\",\"type\":\"webhook\"}" > /dev/null || true
done

# Send webhook events (use first integration if available)
IDS=$(curl -s "${API}/api/integrations" | python3 -c "import sys,json; d=json.load(sys.stdin); print(' '.join(x['id'] for x in d[:5]))" 2>/dev/null || echo "")
for iid in $IDS; do
  for j in 1 2 3; do
    curl -s -X POST "${API}/api/webhook/${iid}" -H "Content-Type: application/json" \
      -d "{\"source\":\"demo\",\"payload\":{\"batch\":$j}}" > /dev/null
  done
  echo "Sent webhooks to integration $iid"
done

# Also hit generic webhook if no integrations (creates one implicitly - no, we created above)
echo "Demo complete. Dashboard should show non-zero metrics."
