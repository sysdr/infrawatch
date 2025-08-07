#!/bin/bash

echo "🎬 Running Demo"
echo "=============="

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Create sample SSH key
echo "Creating sample SSH key..."
curl -X POST "http://localhost:8000/ssh-keys/" \
     -H "Content-Type: application/json" \
     -d '{"name":"demo-key","key_type":"rsa","expires_days":90}'

# Create sample server
echo "Creating sample server..."
# First get the key ID
KEY_ID=$(curl -s "http://localhost:8000/ssh-keys/" | python -c "import sys, json; data=json.load(sys.stdin); print(data[0]['id'] if data else '')")

if [ ! -z "$KEY_ID" ]; then
    curl -X POST "http://localhost:8000/servers/" \
         -H "Content-Type: application/json" \
         -d "{\"name\":\"demo-server\",\"hostname\":\"localhost\",\"port\":22,\"username\":\"demo\",\"ssh_key_id\":\"$KEY_ID\"}"
fi

echo "✅ Demo data created!"
echo "Visit http://localhost:3000 to see the dashboard"
