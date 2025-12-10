#!/bin/bash

echo "=========================================="
echo "Testing Export UI System"
echo "=========================================="

# Wait for services
echo "Waiting for services to start..."
sleep 5

# Test backend health
echo "Testing backend health..."
curl -f http://localhost:8000/health || echo "Backend health check failed"

# Test export creation
echo "Testing export creation..."
curl -X POST http://localhost:8000/api/exports \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "config": {
      "data_source": "metrics",
      "start_date": "2024-01-01T00:00:00Z",
      "end_date": "2024-01-31T23:59:59Z",
      "format_type": "CSV",
      "filters": {},
      "fields": [],
      "options": {}
    }
  }'

echo ""
echo "Test complete!"
