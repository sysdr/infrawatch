#!/bin/bash

echo "=================================================="
echo "Starting Required Services"
echo "=================================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check and start PostgreSQL
echo "Checking PostgreSQL..."
if command_exists pg_isready; then
    if pg_isready -h localhost -p 5432 -U postgres >/dev/null 2>&1; then
        echo "✓ PostgreSQL is already running"
    else
        echo "⚠️  PostgreSQL is not running. Attempting to start..."
        if command_exists systemctl; then
            sudo systemctl start postgresql 2>/dev/null && echo "✓ PostgreSQL started" || echo "⚠️  Could not start PostgreSQL. Please start manually: sudo systemctl start postgresql"
        elif command_exists service; then
            sudo service postgresql start 2>/dev/null && echo "✓ PostgreSQL started" || echo "⚠️  Could not start PostgreSQL. Please start manually: sudo service postgresql start"
        else
            echo "⚠️  Please start PostgreSQL manually"
        fi
        
        # Wait a moment for PostgreSQL to start
        sleep 2
        
        # Check if database exists, create if not
        if ! psql -h localhost -U postgres -lqt | cut -d \| -f 1 | grep -qw user_management; then
            echo "Creating database 'user_management'..."
            psql -h localhost -U postgres -c "CREATE DATABASE user_management;" 2>/dev/null || echo "⚠️  Could not create database. You may need to run: sudo -u postgres createdb user_management"
        fi
    fi
else
    echo "⚠️  PostgreSQL client tools not found. Please install PostgreSQL."
fi

# Check and start Redis
echo ""
echo "Checking Redis..."
if command_exists redis-cli; then
    if redis-cli ping >/dev/null 2>&1; then
        echo "✓ Redis is already running"
    else
        echo "⚠️  Redis is not running. Attempting to start..."
        if command_exists systemctl; then
            sudo systemctl start redis 2>/dev/null && echo "✓ Redis started" || echo "⚠️  Could not start Redis. Please start manually: sudo systemctl start redis"
        elif command_exists service; then
            sudo service redis start 2>/dev/null && echo "✓ Redis started" || echo "⚠️  Could not start Redis. Please start manually: sudo service redis start"
        else
            echo "⚠️  Starting Redis in background..."
            redis-server --daemonize yes 2>/dev/null && echo "✓ Redis started" || echo "⚠️  Could not start Redis. Please start manually: redis-server &"
        fi
    fi
else
    echo "⚠️  Redis client not found. Redis may not be installed."
fi

echo ""
echo "=================================================="
echo "Service check complete"
echo "=================================================="


