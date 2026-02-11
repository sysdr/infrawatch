#!/bin/bash
set -e
API_BASE="http://localhost:8000/api/v1"
echo "Remediation Actions - Demo"

echo "1. Creating low-risk action (Block IP)..."
curl -s -X POST "$API_BASE/remediation/actions" -H "Content-Type: application/json" \
  -d '{"template_id": 1, "incident_id": "INC-SEC-001", "parameters": {"ip_address": "203.0.113.42", "duration_hours": 24}}' | python3 -m json.tool

sleep 2
echo ""
echo "2. Creating high-risk action (Rotate DB Credentials)..."
curl -s -X POST "$API_BASE/remediation/actions" -H "Content-Type: application/json" \
  -d '{"template_id": 2, "incident_id": "INC-SEC-002", "parameters": {"database_name": "prod_db", "service_name": "api_service"}}' | python3 -m json.tool

sleep 2
echo ""
echo "3. Getting statistics..."
curl -s "$API_BASE/remediation/stats" | python3 -m json.tool

echo ""
echo "4. Approving pending action (ID 2)..."
curl -s -X POST "$API_BASE/remediation/actions/2/approve" -H "Content-Type: application/json" \
  -d '{"action_id": 2, "approver": "admin@company.com", "comments": "Approved"}' | python3 -m json.tool

sleep 3
echo ""
echo "5. Final statistics..."
curl -s "$API_BASE/remediation/stats" | python3 -m json.tool

echo ""
echo "Demo complete! Check http://localhost:3000 for dashboard with updated metrics."
