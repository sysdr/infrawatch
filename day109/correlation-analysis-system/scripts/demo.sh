#!/bin/bash

set -e

echo "=========================================="
echo "Running Demonstration"
echo "=========================================="

API_URL="http://localhost:8000"

echo "1. Generating sample metrics..."
curl -X POST "$API_URL/api/correlation/metrics/generate-sample" | python3 -m json.tool

echo ""
echo "2. Detecting correlations..."
sleep 2
curl -X POST "$API_URL/api/correlation/detect" | python3 -m json.tool

echo ""
echo "3. Analyzing root causes..."
sleep 2
curl -X POST "$API_URL/api/correlation/analyze/root-cause" | python3 -m json.tool

echo ""
echo "4. Getting dashboard summary..."
sleep 2
curl -X GET "$API_URL/api/correlation/dashboard/summary" | python3 -m json.tool

echo ""
echo "=========================================="
echo "Demo completed!"
echo "Open http://localhost:3000 to see the dashboard"
echo "=========================================="
