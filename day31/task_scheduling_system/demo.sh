#!/bin/bash

echo "🎬 Task Scheduling System Demo"
echo "=============================="

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Create demo tasks
echo "📝 Creating demo tasks..."

# Task 1: System metrics collection (every 5 minutes)
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "System Metrics Collection",
    "task_function": "collect_system_metrics",
    "cron_expression": "*/5 * * * *",
    "priority": 5,
    "max_retries": 3,
    "timeout_seconds": 60
  }' && echo ""

# Task 2: Usage report generation (every hour)
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Usage Report Generation",
    "task_function": "generate_usage_report",
    "cron_expression": "0 * * * *",
    "priority": 3,
    "max_retries": 2,
    "timeout_seconds": 300
  }' && echo ""

# Task 3: Log cleanup (daily at 2 AM)
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Log Cleanup",
    "task_function": "cleanup_old_logs",
    "cron_expression": "0 2 * * *",
    "priority": 2,
    "max_retries": 1,
    "timeout_seconds": 180
  }' && echo ""

# Task 4: Database backup (weekly on Sunday)
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Database Backup",
    "task_function": "database_backup",
    "cron_expression": "0 0 * * 0",
    "priority": 10,
    "max_retries": 3,
    "timeout_seconds": 1800
  }' && echo ""

echo ""
echo "✅ Demo tasks created successfully!"
echo ""
echo "🌐 Access the dashboard at: http://localhost:3000"
echo "📊 View API documentation at: http://localhost:8000/docs"
echo ""
echo "📈 Monitor task executions:"
echo "   curl http://localhost:8000/api/executions"
echo ""
echo "🔄 View active tasks:"
echo "   curl http://localhost:8000/api/tasks"
