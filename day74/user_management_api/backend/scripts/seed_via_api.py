#!/usr/bin/env python3
"""Seed database via API endpoints"""
import requests
import json
import time
from faker import Faker

BASE_URL = "http://localhost:8000/api"
fake = Faker()

def create_user(email, username, full_name, password):
    """Create a user via API"""
    response = requests.post(
        f"{BASE_URL}/users",
        json={
            "email": email,
            "username": username,
            "full_name": full_name,
            "password": password
        }
    )
    if response.status_code == 201:
        return response.json()
    elif response.status_code == 400 and "already exists" in response.text:
        # User exists, try to get it
        users = requests.get(f"{BASE_URL}/users").json()
        for user in users.get("users", []):
            if user["email"] == email:
                return user
    return None

def create_team(name, description):
    """Create a team via API"""
    response = requests.post(
        f"{BASE_URL}/teams",
        json={"name": name, "description": description}
    )
    if response.status_code == 201:
        return response.json()
    return None

def create_activity(user_id, action, resource_type):
    """Create activity via API"""
    response = requests.post(
        f"{BASE_URL}/activity/users/{user_id}",
        json={
            "action": action,
            "resource_type": resource_type,
            "resource_id": str(fake.uuid4()),
            "details": {"ip": fake.ipv4()}
        }
    )
    return response.status_code == 201

def main():
    print("Seeding database via API...")
    
    # Create users
    users = []
    for i in range(10):
        user = create_user(
            email=fake.email(),
            username=f"{fake.user_name()}{i}",
            full_name=fake.name(),
            password="password123"
        )
        if user:
            users.append(user)
            print(f"Created user: {user['username']}")
        time.sleep(0.1)
    
    # Create teams
    teams = []
    for i in range(5):
        team = create_team(
            name=f"{fake.company()} Team",
            description=fake.catch_phrase()
        )
        if team:
            teams.append(team)
            print(f"Created team: {team['name']}")
        time.sleep(0.1)
    
    # Create activities
    for user in users[:5]:
        for action in ['login', 'create_user', 'update_team', 'assign_permission']:
            create_activity(user['id'], action, fake.random_element(['user', 'team', 'permission']))
        print(f"Created activities for user: {user['username']}")
        time.sleep(0.1)
    
    print(f"\nSeeded {len(users)} users, {len(teams)} teams, and activities!")
    
    # Get stats
    stats = requests.get(f"{BASE_URL}/stats").json()
    print(f"\nCurrent stats:")
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    try:
        main()
    except ImportError:
        print("Installing required packages...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "faker", "-q"])
        import requests
        from faker import Faker
        main()

