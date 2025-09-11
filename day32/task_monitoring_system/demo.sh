#!/bin/bash

echo "🎬 Task Monitoring System Demo"
echo "=============================="

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if ! curl -s http://localhost:8000/api/monitoring/health > /dev/null; then
    echo "❌ Backend not ready. Run './build.sh' first"
    exit 1
fi

echo "✅ Services are ready!"
echo ""

# Demo script
echo "🎭 Starting demo sequence..."

# 1. Register demo workers
echo "1️⃣ Registering demo workers..."
for i in {1..3}; do
    curl -s -X POST "http://localhost:8000/api/workers/register?worker_id=demo-worker-$i&name=Demo%20Worker%20$i&host=localhost&port=$((8000+i))" \
    curl -s -X POST "http://localhost:8000/api/workers/demo-worker-$i/heartbeat" \
        -H "Content-Type: application/json" \
        -d "{\"worker_id\":\"demo-worker-$i\",\"cpu_usage\":$((RANDOM%80+10)),\"memory_usage\":$((RANDOM%70+20)),\"task_count\":0,\"is_healthy\":true}" > /dev/null
done

# 2. Create demo tasks
echo "2️⃣ Creating demo tasks..."
for i in {1..10}; do
    curl -s -X POST "http://localhost:8000/api/tasks/" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"Demo Task $i\",\"payload\":{\"demo\":true,\"task_num\":$i},\"priority\":$((RANDOM%5+1))}" > /dev/null
done

# 3. Process some tasks
echo "3️⃣ Processing tasks..."
TASK_IDS=$(curl -s "http://localhost:8000/api/tasks/?status=queued&limit=5" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for task in data[:5]:
    print(task['id'])
")

for task_id in $TASK_IDS; do
    worker_id="demo-worker-$((RANDOM%3+1))"
    curl -s -X POST "http://localhost:8000/api/tasks/$task_id/process?worker_id=$worker_id" > /dev/null
done

# 4. Show results
echo "4️⃣ Demo Results:"
echo ""
echo "📊 Current Metrics:"
curl -s "http://localhost:8000/api/monitoring/metrics" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"  Tasks: {data['tasks']}\" if 'tasks' in data else '  Tasks: Not available')
print(f\"  Workers: {data['workers']}\" if 'workers' in data else '  Workers: Not available')
"

echo ""
echo "🎯 Dashboard URLs:"
echo "   🌐 Main Dashboard: http://localhost:3000"
echo "   📋 Task Management: http://localhost:3000/tasks"
echo "   👥 Worker Status: http://localhost:3000/workers"
echo "   📈 Metrics: http://localhost:3000/metrics"
echo "   🔗 API Documentation: http://localhost:8000/docs"
echo ""
echo "✨ Demo complete! Check the dashboard to see the monitoring in action."
