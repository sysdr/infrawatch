#!/bin/bash
# Run demo: generate sample logs and evaluate retention so dashboard shows non-zero metrics.
# Usage: ./scripts/run_demo.sh [API_BASE]
# Default API_BASE=http://localhost:8000

API_BASE="${1:-http://localhost:8000}"

echo "Demo: Populating dashboard with sample data (API: $API_BASE)"
echo ""

# Health check
if ! curl -sf "$API_BASE/" >/dev/null; then
  echo "ERROR: Backend not reachable at $API_BASE. Start backend first (e.g. docker compose up -d)."
  exit 1
fi

echo "1. Generating 100 sample logs..."
curl -s -X POST "$API_BASE/logs/generate?count=100" | head -1
echo ""

echo "2. Evaluating retention (may create archival jobs)..."
curl -s -X POST "$API_BASE/retention/evaluate" | head -1
echo ""

echo "3. Current stats:"
curl -s "$API_BASE/logs/stats" | python3 -m json.tool 2>/dev/null || curl -s "$API_BASE/logs/stats"
echo ""

echo "Done. Dashboard: http://localhost:3000 (metrics should be non-zero)."
