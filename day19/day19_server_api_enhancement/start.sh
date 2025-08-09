#!/bin/bash
echo "🚀 Starting Day 19: Server API Enhancement..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r backend/requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
cd backend
python -c "
from app.database import engine, Base
from app.models import server_models
import json
from datetime import datetime

# Create tables
Base.metadata.create_all(bind=engine)

# Create sample data
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
db = Session()

# Sample servers
servers = [
    {'name': 'web-server-01', 'hostname': 'web01.example.com', 'ip_address': '10.0.1.10', 'status': 'running', 'region': 'us-east-1', 'instance_type': 't3.medium', 'cpu_cores': 2, 'memory_gb': 4, 'storage_gb': 20, 'os_type': 'ubuntu-20.04', 'tags': {'environment': 'production', 'role': 'web'}},
    {'name': 'api-server-01', 'hostname': 'api01.example.com', 'ip_address': '10.0.1.20', 'status': 'running', 'region': 'us-east-1', 'instance_type': 't3.large', 'cpu_cores': 4, 'memory_gb': 8, 'storage_gb': 40, 'os_type': 'ubuntu-20.04', 'tags': {'environment': 'production', 'role': 'api'}},
    {'name': 'db-server-01', 'hostname': 'db01.example.com', 'ip_address': '10.0.1.30', 'status': 'running', 'region': 'us-east-1', 'instance_type': 't3.xlarge', 'cpu_cores': 8, 'memory_gb': 16, 'storage_gb': 100, 'os_type': 'ubuntu-20.04', 'tags': {'environment': 'production', 'role': 'database'}},
    {'name': 'test-server-01', 'hostname': 'test01.example.com', 'ip_address': '10.0.2.10', 'status': 'stopped', 'region': 'us-west-2', 'instance_type': 't3.small', 'cpu_cores': 1, 'memory_gb': 2, 'storage_gb': 10, 'os_type': 'ubuntu-20.04', 'tags': {'environment': 'testing', 'role': 'web'}},
    {'name': 'staging-server-01', 'hostname': 'staging01.example.com', 'ip_address': '10.0.3.10', 'status': 'running', 'region': 'eu-west-1', 'instance_type': 't3.medium', 'cpu_cores': 2, 'memory_gb': 4, 'storage_gb': 20, 'os_type': 'ubuntu-20.04', 'tags': {'environment': 'staging', 'role': 'web'}}
]

for server_data in servers:
    server = server_models.Server(**server_data)
    db.add(server)

# Sample groups
groups = [
    {'name': 'Production Servers', 'description': 'All production environment servers', 'color': '#dc2626'},
    {'name': 'Web Servers', 'description': 'Frontend web servers', 'color': '#2563eb'},
    {'name': 'Database Servers', 'description': 'Database and storage servers', 'color': '#059669'},
    {'name': 'Testing Environment', 'description': 'Servers for testing and QA', 'color': '#d97706'}
]

for group_data in groups:
    group = server_models.Group(**group_data)
    db.add(group)

# Sample templates
templates = [
    {
        'name': 'Web Server Template',
        'description': 'Standard configuration for web servers',
        'config': {
            'instance_type': 't3.medium',
            'cpu_cores': 2,
            'memory_gb': 4,
            'storage_gb': 20,
            'os_type': 'ubuntu-20.04',
            'region': 'us-east-1',
            'tags': {'role': 'web', 'managed_by': 'template'}
        }
    },
    {
        'name': 'API Server Template',
        'description': 'Standard configuration for API servers',
        'config': {
            'instance_type': 't3.large',
            'cpu_cores': 4,
            'memory_gb': 8,
            'storage_gb': 40,
            'os_type': 'ubuntu-20.04',
            'region': 'us-east-1',
            'tags': {'role': 'api', 'managed_by': 'template'}
        }
    }
]

for template_data in templates:
    template = server_models.Template(**template_data)
    db.add(template)

db.commit()
db.close()
print('✅ Sample data created successfully')
"

# Start FastAPI server
echo "🚀 Starting FastAPI server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd ../frontend

# Install Node dependencies and start React app
echo "⚛️ Installing Node dependencies..."
npm install

echo "🚀 Starting React development server..."
npm start &
FRONTEND_PID=$!

# Save PIDs for cleanup
echo $BACKEND_PID > ../backend.pid
echo $FRONTEND_PID > ../frontend.pid

echo "✅ Application started successfully!"
echo "🌐 Frontend: http://localhost:3000"
echo "📡 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user input
wait
