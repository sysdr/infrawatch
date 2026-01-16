#!/bin/bash

# Database initialization script
set -e

echo "Initializing database..."

# Try to connect and create database if it doesn't exist
python3 << 'PYTHON_EOF'
import asyncio
import asyncpg
import sys

async def init_database():
    try:
        # Try connecting to postgres database first
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            database='postgres',
            password=''  # Try without password first
        )
        
        # Check if database exists
        db_exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = 'api_security_db'"
        )
        
        if not db_exists:
            # Create database
            await conn.execute("CREATE DATABASE api_security_db")
            print("✓ Database 'api_security_db' created")
        else:
            print("✓ Database 'api_security_db' already exists")
        
        # Check if user exists
        user_exists = await conn.fetchval(
            "SELECT 1 FROM pg_user WHERE usename = 'apiuser'"
        )
        
        if not user_exists:
            # Create user
            await conn.execute(
                "CREATE USER apiuser WITH PASSWORD 'apipass123'"
            )
            print("✓ User 'apiuser' created")
        else:
            print("✓ User 'apiuser' already exists")
        
        # Grant privileges
        await conn.execute(
            "GRANT ALL PRIVILEGES ON DATABASE api_security_db TO apiuser"
        )
        print("✓ Privileges granted")
        
        await conn.close()
        
    except Exception as e:
        print(f"Note: Cannot auto-create database: {e}")
        print("You may need to create it manually:")
        print("  sudo -u postgres psql -c \"CREATE USER apiuser WITH PASSWORD 'apipass123';\"")
        print("  sudo -u postgres psql -c \"CREATE DATABASE api_security_db OWNER apiuser;\"")
        sys.exit(0)  # Non-fatal error

asyncio.run(init_database())
PYTHON_EOF

echo "Database initialization complete"
