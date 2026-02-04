#!/usr/bin/env python3
import asyncio
import aiohttp
import random
from datetime import datetime
import sys

API_URL = "http://localhost:8000/api/logs"
SERVICES = ["auth-api", "user-service", "payment-service", "notification-service"]
LEVELS = ["DEBUG", "INFO", "WARN", "ERROR"]
MESSAGES = [
    "User login successful",
    "Authentication failed",
    "Payment processed",
    "Database connection established",
    "API request received",
    "Cache miss for key",
    "Background job completed",
    "Rate limit exceeded"
]

async def generate_log():
    async with aiohttp.ClientSession() as session:
        log = {
            "level": random.choice(LEVELS),
            "service": random.choice(SERVICES),
            "message": random.choice(MESSAGES),
            "metadata": {
                "user_id": f"user_{random.randint(1000, 9999)}",
                "ip": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                "endpoint": f"/api/{random.choice(['users', 'payments', 'auth'])}"
            }
        }

        try:
            async with session.post(API_URL, json=log) as response:
                if response.status == 201:
                    print(f"✅ Generated: [{log['level']}] {log['service']} - {log['message']}")
                else:
                    print(f"❌ Failed: {response.status}")
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    rate = float(sys.argv[2]) if len(sys.argv) > 2 else 10

    print(f"🚀 Generating {count} logs at {rate} logs/second...")

    for _ in range(count):
        asyncio.create_task(generate_log())
        await asyncio.sleep(1.0 / rate)

    await asyncio.sleep(2)
    print(f"✅ Generated {count} logs")

if __name__ == "__main__":
    asyncio.run(main())
