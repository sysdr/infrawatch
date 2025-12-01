#!/bin/bash

echo "=========================================="
echo "Building Notification Analytics API"
echo "=========================================="

# Backend setup
echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "Initializing database..."
# Wait for PostgreSQL to be ready (try multiple connection methods)
DB_CONNECTED=false
for i in {1..10}; do
  if python3 -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('postgresql://postgres:postgres@127.0.0.1:5432/postgres'))" 2>/dev/null; then
    DB_CONNECTED=true
    break
  fi
  echo "Waiting for PostgreSQL... (attempt $i/10)"
  sleep 2
done

if [ "$DB_CONNECTED" = false ]; then
  echo "Warning: Could not connect to PostgreSQL. You may need to:"
  echo "  1. Start PostgreSQL: sudo systemctl start postgresql"
  echo "  2. Configure PostgreSQL to accept TCP connections"
  echo "  3. Or use Docker Compose: docker-compose up -d postgres redis"
  echo "Continuing anyway..."
fi

# Create database
python3 -c "
import asyncio
import asyncpg

async def create_db():
    conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/postgres')
    try:
        await conn.execute('CREATE DATABASE notification_analytics')
        print('Database created')
    except:
        print('Database already exists')
    finally:
        await conn.close()

asyncio.run(create_db())
"

# Initialize schema
export PYTHONPATH="${PWD}:${PYTHONPATH}"
python3 -c "
import asyncio
import sys
sys.path.insert(0, '.')
from database.db_config import init_db
asyncio.run(init_db())
print('Schema initialized')
"

# Seed data
echo "Seeding test data..."
export PYTHONPATH="${PWD}:${PYTHONPATH}"
python3 seed_data.py

echo "Starting backend server..."
export PYTHONPATH="${PWD}:${PYTHONPATH}"
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd ..

# Frontend setup
echo "Setting up frontend..."
cd frontend
npm install
echo "Starting frontend server..."
PORT=3000 npm start &
FRONTEND_PID=$!

cd ..

echo ""
echo "=========================================="
echo "System Started Successfully!"
echo "=========================================="
echo "Backend API: http://localhost:8000"
echo "Frontend Dashboard: http://localhost:3000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Save PIDs for stop script
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

wait
