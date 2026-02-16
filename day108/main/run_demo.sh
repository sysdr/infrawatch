#!/bin/bash
# Demo script - seed metrics and run calculations (idempotent: safe to run multiple times)
set -e
API_URL="${API_URL:-http://localhost:8000}"

echo "=========================================="
echo "Custom Metrics Engine - Demo Execution"
echo "=========================================="

echo "Waiting for backend at $API_URL..."
for i in {1..30}; do
    if curl -s "$API_URL/health" >/dev/null 2>&1; then
        echo "Backend is ready."
        break
    fi
    sleep 1
    [ $i -eq 30 ] && { echo "ERROR: Backend not available"; exit 1; }
done

echo ""
echo "Ensuring demo metrics exist..."

# Helper: create metric only if not exists (ignore 409 = already exists)
ensure_metric() {
    local name="$1"
    local payload="$2"
    # Check if metric exists
    if curl -s "$API_URL/api/metrics/definitions" | python3 -c "
import sys,json
try:
    m=json.load(sys.stdin)
    names=[x['name'] for x in m]
    sys.exit(0 if sys.argv[1] in names else 1)
except: sys.exit(1)
" "$name" 2>/dev/null; then
        echo "  - $name (already exists)"
        return 0
    fi
    # Create
    local resp
    resp=$(curl -s -w "%{http_code}" -X POST "$API_URL/api/metrics/definitions" \
        -H "Content-Type: application/json" \
        -d "$payload" 2>/dev/null)
    local code="${resp: -3}"
    if [ "$code" = "200" ] || [ "$code" = "201" ]; then
        echo "  - $name (created)"
    elif [ "$code" = "409" ]; then
        echo "  - $name (already exists)"
    else
        echo "  - $name (create failed, continuing...)"
    fi
}

ensure_metric "profit_margin" '{"name":"profit_margin","display_name":"Profit Margin","formula":"(revenue - cost) / revenue * 100","variables":["revenue","cost"],"category":"financial","unit":"%","aggregation_type":"avg"}'
ensure_metric "roi" '{"name":"roi","display_name":"ROI","formula":"(gain - cost) / cost * 100","variables":["gain","cost"],"category":"financial","unit":"%","aggregation_type":"avg"}'
ensure_metric "revenue_per_unit" '{"name":"revenue_per_unit","display_name":"Revenue Per Unit","formula":"revenue / units","variables":["revenue","units"],"category":"operational","unit":"$","aggregation_type":"avg"}'

echo ""
echo "Running calculations..."
METRIC_IDS=$(curl -s "$API_URL/api/metrics/definitions" | python3 -c "import sys,json; m=json.load(sys.stdin); print(' '.join(x['id'] for x in m))" 2>/dev/null || echo "")

for mid in $METRIC_IDS; do
    NAME=$(curl -s "$API_URL/api/metrics/definitions/$mid" | python3 -c "import sys,json; print(json.load(sys.stdin).get('name',''))" 2>/dev/null)
    case "$NAME" in
        profit_margin) curl -s -X POST "$API_URL/api/metrics/calculate/$mid" -H "Content-Type: application/json" -d '{"input_values":{"revenue":10000,"cost":6000}}' >/dev/null ;;
        roi) curl -s -X POST "$API_URL/api/metrics/calculate/$mid" -H "Content-Type: application/json" -d '{"input_values":{"gain":1500,"cost":1000}}' >/dev/null ;;
        revenue_per_unit) curl -s -X POST "$API_URL/api/metrics/calculate/$mid" -H "Content-Type: application/json" -d '{"input_values":{"revenue":50000,"units":1000}}' >/dev/null ;;
    esac
done

echo ""
echo "Demo complete! Open http://localhost:3000"
echo "=========================================="
