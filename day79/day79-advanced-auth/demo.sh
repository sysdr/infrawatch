#!/bin/bash

# Demo script to populate data for dashboard validation

API_URL="http://localhost:8000/api/auth"

echo "=================================================="
echo "Running Demo to Populate Dashboard Data"
echo "=================================================="

# Register a test user
echo ""
echo "1. Registering test user..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/register?email=demo@example.com&username=demouser&password=DemoPass123!")

USER_ID=$(echo $REGISTER_RESPONSE | grep -o '"user_id":"[^"]*' | cut -d'"' -f4)
echo "User registered with ID: $USER_ID"

if [ -z "$USER_ID" ]; then
  echo "User might already exist, trying to login to get session..."
  # Try to login to get user info from session
  LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=demouser&password=DemoPass123!")
  
  # Extract user_id from JWT token (we'll use a workaround - query DB or use session)
  # For demo purposes, we'll use the session_id to query
  SESSION_ID=$(echo $LOGIN_RESPONSE | grep -o '"session_id":"[^"]*' | cut -d'"' -f4)
  if [ -n "$SESSION_ID" ]; then
    echo "Got session, using demo-user-id for API calls"
    USER_ID="demo-user-id"
  else
    echo "Using default user ID for demo"
    USER_ID="demo-user-id"
  fi
fi

echo ""
echo "2. Creating multiple login attempts to generate risk events..."

# Create several login attempts with different scenarios
for i in {1..5}; do
  echo "  Login attempt $i..."
  curl -s -X POST "$API_URL/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=demouser&password=DemoPass123!" > /dev/null
  sleep 1
done

echo ""
echo "3. Registering device fingerprint..."
DEVICE_DATA='{"userAgent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36","language":"en-US","platform":"Linux x86_64","screen":"1920x1080x24","timezone":"America/New_York"}'

curl -s -X POST "$API_URL/device/fingerprint?user_id=$USER_ID" \
  -H "Content-Type: application/json" \
  -d "$DEVICE_DATA" > /dev/null

echo ""
echo "4. Creating sessions..."
# Create multiple sessions by logging in
for i in {1..3}; do
  echo "  Creating session $i..."
  curl -s -X POST "$API_URL/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=demouser&password=DemoPass123!" > /dev/null
  sleep 0.5
done

echo ""
echo "5. Fetching risk history..."
RISK_HISTORY=$(curl -s "$API_URL/risk/history?user_id=$USER_ID&limit=10")
echo "Risk events found: $(echo $RISK_HISTORY | grep -o '"risk_score"' | wc -l)"

echo ""
echo "6. Fetching sessions..."
SESSIONS=$(curl -s "$API_URL/sessions?user_id=$USER_ID")
SESSION_COUNT=$(echo $SESSIONS | grep -o '"session_id"' | wc -l)
echo "Active sessions: $SESSION_COUNT"

echo ""
echo "=================================================="
echo "Demo Complete!"
echo "=================================================="
echo ""
echo "Dashboard should now show:"
echo "  - Risk events with scores"
echo "  - Active sessions"
echo "  - Device information"
echo ""
echo "Visit http://localhost:3000 to view the dashboard"
echo ""
