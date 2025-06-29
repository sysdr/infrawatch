#!/usr/bin/env python3
"""
Script to set up test database for RBAC system tests
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_test_database():
    """Create test database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="password",
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if test database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='rbac_test'")
        exists = cursor.fetchone()
        
        if not exists:
            print("🔧 Creating test database 'rbac_test'...")
            cursor.execute("CREATE DATABASE rbac_test")
            print("✅ Test database created successfully!")
        else:
            print("✅ Test database 'rbac_test' already exists!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating test database: {e}")
        print("Make sure PostgreSQL is running and accessible")
        return False
    
    return True

if __name__ == "__main__":
    create_test_database() 