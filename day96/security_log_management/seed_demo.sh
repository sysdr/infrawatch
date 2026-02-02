#!/bin/bash
API_URL="${API_URL:-http://localhost:8000/api}"
echo "Seeding demo security events to $API_URL (ensure backend is running)"
for i in 1 2 3 4 5 6 7 8 9 10; do
  curl -s -X POST "$API_URL/security/events" -H "Content-Type: application/json" -d "{
    \"event_type\": \"authentication\",
    \"severity\": \"medium\",
    \"user_id\": \"user$i\",
    \"username\": \"demouser$i\",
    \"ip_address\": \"192.168.1.$i\",
    \"resource\": \"/api/login\",
    \"action\": \"login\",
    \"result\": \"success\",
    \"details\": {\"method\": \"password\"}
  }" > /dev/null
done
# One failed login to trigger potential threat
curl -s -X POST "$API_URL/security/events" -H "Content-Type: application/json" -d '{"event_type":"authentication","severity":"high","user_id":"user99","username":"attacker","ip_address":"10.0.0.1","resource":"/api/login","action":"login","result":"failure","details":{}}' > /dev/null
echo "Demo seed complete. Refresh dashboard to see metrics."
