#!/usr/bin/env python3
"""
Demo data script to populate the server management system
"""
import requests
import json
import time

API_BASE = "http://localhost:8000"

def create_demo_servers():
    """Create demo servers for testing"""
    demo_servers = [
        {
            "name": "web-server-01",
            "hostname": "web01.example.com",
            "ip_address": "192.168.1.10",
            "server_type": "web",
            "environment": "production",
            "region": "us-east-1",
            "specs": {"cpu": "4 cores", "memory": "8GB", "disk": "100GB SSD"},
            "tags": ["web", "nginx", "production"],
            "tenant_id": "default"
        },
        {
            "name": "db-server-01",
            "hostname": "db01.example.com",
            "ip_address": "192.168.1.20",
            "server_type": "database",
            "environment": "production",
            "region": "us-east-1",
            "specs": {"cpu": "8 cores", "memory": "32GB", "disk": "500GB SSD"},
            "tags": ["database", "postgresql", "production"],
            "tenant_id": "default"
        },
        {
            "name": "api-server-01",
            "hostname": "api01.example.com",
            "ip_address": "192.168.1.30",
            "server_type": "api",
            "environment": "production",
            "region": "us-west-1",
            "specs": {"cpu": "6 cores", "memory": "16GB", "disk": "200GB SSD"},
            "tags": ["api", "fastapi", "production"],
            "tenant_id": "default"
        },
        {
            "name": "cache-server-01",
            "hostname": "cache01.example.com",
            "ip_address": "192.168.1.40",
            "server_type": "cache",
            "environment": "production",
            "region": "us-west-1",
            "specs": {"cpu": "2 cores", "memory": "8GB", "disk": "50GB SSD"},
            "tags": ["cache", "redis", "production"],
            "tenant_id": "default"
        },
        {
            "name": "test-server-01",
            "hostname": "test01.example.com",
            "ip_address": "192.168.2.10",
            "server_type": "web",
            "environment": "testing",
            "region": "us-east-1",
            "specs": {"cpu": "2 cores", "memory": "4GB", "disk": "50GB SSD"},
            "tags": ["web", "testing"],
            "tenant_id": "default"
        }
    ]
    
    created_servers = []
    for server_data in demo_servers:
        try:
            response = requests.post(f"{API_BASE}/api/servers/", json=server_data)
            if response.status_code == 200:
                server = response.json()
                created_servers.append(server)
                print(f"✅ Created server: {server['name']} (ID: {server['id']})")
            else:
                print(f"❌ Failed to create server {server_data['name']}: {response.text}")
        except Exception as e:
            print(f"❌ Error creating server {server_data['name']}: {str(e)}")
    
    return created_servers

def demo_operations(servers):
    """Demonstrate CRUD operations"""
    if not servers:
        print("No servers to demonstrate operations")
        return
    
    # Update a server
    server_to_update = servers[0]
    update_data = {"status": "maintenance"}
    
    try:
        response = requests.put(f"{API_BASE}/api/servers/{server_to_update['id']}", json=update_data)
        if response.status_code == 200:
            print(f"✅ Updated server {server_to_update['name']} to maintenance mode")
        else:
            print(f"❌ Failed to update server: {response.text}")
    except Exception as e:
        print(f"❌ Error updating server: {str(e)}")
    
    # List servers with filters
    try:
        response = requests.get(f"{API_BASE}/api/servers/?environment=production")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data['servers'])} production servers")
        else:
            print(f"❌ Failed to list servers: {response.text}")
    except Exception as e:
        print(f"❌ Error listing servers: {str(e)}")
    
    # Get audit logs
    try:
        response = requests.get(f"{API_BASE}/api/servers/{server_to_update['id']}/audit")
        if response.status_code == 200:
            logs = response.json()
            print(f"✅ Retrieved {len(logs)} audit log entries for server {server_to_update['name']}")
        else:
            print(f"❌ Failed to get audit logs: {response.text}")
    except Exception as e:
        print(f"❌ Error getting audit logs: {str(e)}")

if __name__ == "__main__":
    print("🎬 Starting demo data creation...")
    print("⏳ Waiting for API to be ready...")
    
    # Wait for API to be ready
    for i in range(30):
        try:
            response = requests.get(f"{API_BASE}/")
            if response.status_code == 200:
                break
        except:
            pass
        time.sleep(1)
    else:
        print("❌ API not ready after 30 seconds")
        exit(1)
    
    print("✅ API is ready!")
    
    # Create demo servers
    servers = create_demo_servers()
    
    # Demonstrate operations
    print("\n🎭 Demonstrating operations...")
    demo_operations(servers)
    
    print("\n🎉 Demo completed!")
    print("📊 Visit http://localhost:3000 to see the dashboard")
    print("🔧 Visit http://localhost:8000/docs to see the API documentation")
