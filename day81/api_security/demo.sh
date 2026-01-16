#!/bin/bash

# Demo script to generate API requests and populate dashboard metrics
set -e

API_URL="http://localhost:8000"
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}API Security System - Demo Script${NC}"
echo -e "${BLUE}========================================${NC}"

# Step 1: Create an API key
echo -e "${YELLOW}Step 1: Creating API key...${NC}"
RESPONSE=$(curl -s -X POST "${API_URL}/admin/api-keys" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo API Key",
    "description": "Key for demonstration purposes",
    "rate_limit": 100,
    "rate_window": 60,
    "expires_in_days": 90
  }')

API_KEY=$(echo "$RESPONSE" | grep -o '"full_key":"[^"]*' | cut -d'"' -f4)

if [ -z "$API_KEY" ]; then
    echo -e "${YELLOW}Warning: Could not extract API key. Trying alternative method...${NC}"
    API_KEY=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('full_key', ''))" 2>/dev/null || echo "")
fi

if [ -z "$API_KEY" ]; then
    echo "Response: $RESPONSE"
    echo "Error: Could not create API key. Is the backend running?"
    exit 1
fi

echo -e "${GREEN}✓ API Key created: ${API_KEY:0:30}...${NC}"

# Step 2: Make multiple API requests to populate metrics
echo -e "${YELLOW}Step 2: Making API requests to populate dashboard...${NC}"

for i in {1..20}; do
    curl -s -X GET "${API_URL}/api/protected/data" \
      -H "X-API-Key: ${API_KEY}" > /dev/null
    if [ $((i % 5)) -eq 0 ]; then
        echo -e "  Made ${i} requests..."
    fi
done

echo -e "${GREEN}✓ Made 20 API requests${NC}"

# Step 3: Test rate limiting (make many requests)
echo -e "${YELLOW}Step 3: Testing rate limiting (making many requests)...${NC}"

RATE_LIMITED=0
for i in {1..150}; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
      -X GET "${API_URL}/api/protected/data" \
      -H "X-API-Key: ${API_KEY}")
    
    if [ "$STATUS" = "429" ]; then
        RATE_LIMITED=$((RATE_LIMITED + 1))
    fi
    
    if [ $((i % 25)) -eq 0 ]; then
        echo -e "  Made ${i} requests (${RATE_LIMITED} rate limited)..."
    fi
done

echo -e "${GREEN}✓ Made 150 requests (${RATE_LIMITED} were rate limited)${NC}"

# Step 4: Check analytics
echo -e "${YELLOW}Step 4: Fetching analytics...${NC}"
ANALYTICS=$(curl -s "${API_URL}/admin/analytics/rate-limits?hours=24" \
  -H "X-API-Key: ${API_KEY}")

TOTAL_REQUESTS=$(echo "$ANALYTICS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(sum(s['total_requests'] for s in data) if isinstance(data, list) else 0)" 2>/dev/null || echo "0")

echo -e "${GREEN}✓ Analytics retrieved (Total requests: ${TOTAL_REQUESTS})${NC}"

# Step 5: Check request logs
echo -e "${YELLOW}Step 5: Fetching request logs...${NC}"
LOGS=$(curl -s "${API_URL}/admin/request-logs?limit=10" \
  -H "X-API-Key: ${API_KEY}")

LOG_COUNT=$(echo "$LOGS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data) if isinstance(data, list) else 0)" 2>/dev/null || echo "0")

echo -e "${GREEN}✓ Request logs retrieved (Showing ${LOG_COUNT} recent logs)${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Demo completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Dashboard URL: http://localhost:3000${NC}"
echo -e "${BLUE}API Docs: http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}The dashboard should now show:${NC}"
echo -e "  - Total requests: ${TOTAL_REQUESTS}+"
echo -e "  - Rate limited requests: ${RATE_LIMITED}+"
echo -e "  - Request logs with timestamps"
echo -e "  - Analytics charts with data"
echo ""
