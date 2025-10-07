#!/bin/bash

set -e

echo "🎯 Running Alert Rules API Demo..."

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
until curl -s http://localhost:8000/health > /dev/null; do
    echo "Waiting for backend..."
    sleep 2
done

echo "✅ Backend is ready!"

# Initialize default templates
echo "📝 Initializing default templates..."
curl -X POST http://localhost:8000/api/v1/templates/initialize-defaults

# Create sample rules
echo "🔧 Creating sample alert rules..."

# CPU Utilization Rule
curl -X POST http://localhost:8000/api/v1/rules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "High CPU Utilization",
    "description": "Alert when CPU usage exceeds 85%",
    "expression": "avg(cpu_usage_percent) > {threshold}",
    "severity": "warning",
    "enabled": true,
    "tags": ["infrastructure", "cpu"],
    "thresholds": {"threshold": 85}
  }'

# Memory Utilization Rule
curl -X POST http://localhost:8000/api/v1/rules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "High Memory Usage",
    "description": "Alert when memory usage exceeds 90%",
    "expression": "avg(memory_usage_percent) > {threshold}",
    "severity": "critical",
    "enabled": true,
    "tags": ["infrastructure", "memory"],
    "thresholds": {"threshold": 90}
  }'

# API Response Time Rule
curl -X POST http://localhost:8000/api/v1/rules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Slow API Response",
    "description": "Alert when API response time exceeds 2 seconds",
    "expression": "avg(response_time_ms) > {threshold}",
    "severity": "warning",
    "enabled": true,
    "tags": ["application", "performance"],
    "thresholds": {"threshold": 2000}
  }'

echo "🧪 Running rule tests..."

# Test CPU rule
curl -X POST http://localhost:8000/api/v1/test/rule \
  -H "Content-Type: application/json" \
  -d '{
    "rule_id": 1,
    "test_data": [
      {"cpu_usage_percent": 45.2},
      {"cpu_usage_percent": 89.7},
      {"cpu_usage_percent": 92.1}
    ],
    "expected_results": [false, true, true]
  }'

echo "📊 Fetching rules summary..."
curl -X GET http://localhost:8000/api/v1/rules

echo ""
echo "🎉 Demo completed successfully!"
echo "🌐 Open http://localhost:3000 to view the dashboard"
echo "📚 Open http://localhost:8000/docs to view API documentation"
echo "🔍 Check the frontend dashboard to see the created rules and test results"
