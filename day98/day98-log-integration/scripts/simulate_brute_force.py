#!/usr/bin/env python3
import asyncio
import aiohttp
import random
from datetime import datetime

API_URL = "http://localhost:8000/api/logs"

async def simulate_attack(user_id, num_attempts, num_ips):
    print(f"🔴 Simulating brute force attack on user: {user_id}")
    print(f"   Attempts: {num_attempts}, Unique IPs: {num_ips}")

    ips = [f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}" for _ in range(num_ips)]

    async with aiohttp.ClientSession() as session:
        for i in range(num_attempts):
            log = {
                "level": "ERROR",
                "service": "auth-api",
                "message": f"authentication failed for user {user_id}",
                "metadata": {
                    "user_id": user_id,
                    "ip": random.choice(ips),
                    "endpoint": "/api/auth/login"
                }
            }

            try:
                await session.post(API_URL, json=log)
                print(f"  Attack attempt {i+1}/{num_attempts}")
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"❌ Error: {e}")

    print("🔴 Attack simulation complete. Check alerts in dashboard.")

if __name__ == "__main__":
    import sys
    user = sys.argv[1] if len(sys.argv) > 1 else "testuser"
    attempts = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    ips = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    asyncio.run(simulate_attack(user, attempts, ips))
