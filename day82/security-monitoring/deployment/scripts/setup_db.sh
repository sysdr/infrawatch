#!/bin/bash

# Database setup script
# This script creates the database and user for security monitoring

echo "Setting up database for Security Monitoring System..."

# Try to create database using postgres user
# Note: This may require sudo access or postgres user permissions

DB_NAME="security_monitoring"
DB_USER="security_user"
DB_PASS="security_pass"

# Check if we can connect as postgres user
if psql -U postgres -c "SELECT 1;" > /dev/null 2>&1; then
    echo "Connected as postgres user"
    
    # Create user if it doesn't exist
    psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" 2>&1 | grep -v "already exists" || echo "User $DB_USER already exists"
    
    # Create database if it doesn't exist
    psql -U postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>&1 | grep -v "already exists" || echo "Database $DB_NAME already exists"
    
    # Grant privileges
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>&1
    
    echo "Database setup complete!"
else
    echo "Cannot connect as postgres user. Trying alternative methods..."
    echo "You may need to run: sudo -u postgres psql"
    echo "Then execute:"
    echo "  CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
    echo "  CREATE DATABASE $DB_NAME OWNER $DB_USER;"
    echo "  GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
fi
