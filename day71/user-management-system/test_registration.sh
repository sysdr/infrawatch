#!/bin/bash

echo "=================================================="
echo "Testing Registration and Login"
echo "=================================================="

# Test Registration
echo ""
echo "1. Testing Registration..."
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser'$(date +%s)'@example.com","password":"testpass123"}')

echo "Response: $REGISTER_RESPONSE"

if echo "$REGISTER_RESPONSE" | grep -q "id"; then
    echo "✅ Registration successful!"
    EMAIL=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['email'])" 2>/dev/null || echo "testuser@example.com")
else
    echo "❌ Registration failed"
    EMAIL="testuser@example.com"
fi

# Test Login
echo ""
echo "2. Testing Login..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"testpass123\"}")

echo "Response: $LOGIN_RESPONSE"

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo "✅ Login successful!"
else
    echo "❌ Login failed"
fi

echo ""
echo "=================================================="
echo "Test Complete"
echo "=================================================="


