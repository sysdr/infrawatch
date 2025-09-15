#!/bin/bash

echo "🎭 Running Task Orchestration System Demo..."

# Check if backend is running
if ! curl -s http://localhost:8000/api/v1/health > /dev/null; then
    echo "❌ Backend not running. Please run ./build.sh first"
    exit 1
fi

echo "📝 Creating sample workflows..."

# Create e-commerce workflow
echo "🛒 Creating e-commerce workflow..."
ECOMMERCE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/workflows/samples/ecommerce)
ECOMMERCE_ID=$(echo $ECOMMERCE_RESPONSE | grep -o '"workflow_id":"[^"]*' | cut -d'"' -f4)

# Create blog workflow  
echo "📝 Creating blog workflow..."
BLOG_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/workflows/samples/blog)
BLOG_ID=$(echo $BLOG_RESPONSE | grep -o '"workflow_id":"[^"]*' | cut -d'"' -f4)

echo "▶️ Executing workflows..."

# Execute e-commerce workflow
curl -s -X POST http://localhost:8000/api/v1/workflows/$ECOMMERCE_ID/execute
echo "🛒 E-commerce workflow execution started"

# Wait a bit
sleep 2

# Execute blog workflow
curl -s -X POST http://localhost:8000/api/v1/workflows/$BLOG_ID/execute  
echo "📝 Blog workflow execution started"

echo ""
echo "✅ Demo workflows created and executing!"
echo ""
echo "🔍 Monitor progress:"
echo "   Frontend: http://localhost:3000"
echo "   E-commerce status: curl http://localhost:8000/api/v1/workflows/$ECOMMERCE_ID/status"
echo "   Blog status: curl http://localhost:8000/api/v1/workflows/$BLOG_ID/status"
echo "   All workflows: curl http://localhost:8000/api/v1/workflows"
echo "   Metrics: curl http://localhost:8000/api/v1/metrics"
