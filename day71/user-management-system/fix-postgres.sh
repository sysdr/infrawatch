#!/bin/bash

echo "=================================================="
echo "Fixing PostgreSQL Connection Issue"
echo "=================================================="

# Check if Docker is available and use it
if command -v docker >/dev/null 2>&1 && command -v docker-compose >/dev/null 2>&1; then
    echo "Using Docker to start PostgreSQL..."
    cd docker
    docker-compose up -d postgres redis
    echo "✓ PostgreSQL and Redis started via Docker"
    echo ""
    echo "Wait a few seconds for services to start, then test registration."
    exit 0
fi

# Alternative: Try to fix local PostgreSQL
echo "Attempting to fix local PostgreSQL configuration..."

# Check if we can connect via Unix socket
if psql -U postgres -d postgres -c "SELECT 1;" >/dev/null 2>&1; then
    echo "✓ Can connect via Unix socket"
    
    # Try to create database if it doesn't exist
    psql -U postgres -d postgres -c "CREATE DATABASE user_management;" 2>/dev/null || echo "Database may already exist"
    
    # Check PostgreSQL config
    echo "Checking PostgreSQL listen_addresses..."
    sudo -u postgres psql -d postgres -c "SHOW listen_addresses;" 2>/dev/null || echo "Cannot check config"
    
    echo ""
    echo "If PostgreSQL is not accepting TCP connections, you may need to:"
    echo "1. Edit /etc/postgresql/*/main/postgresql.conf"
    echo "2. Set listen_addresses = 'localhost' or '*'"
    echo "3. Restart PostgreSQL: sudo systemctl restart postgresql"
else
    echo "⚠️  Cannot connect to PostgreSQL"
    echo ""
    echo "Please start PostgreSQL manually:"
    echo "  sudo systemctl start postgresql"
    echo "  OR use Docker: ./build.sh docker"
fi


