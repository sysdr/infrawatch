#!/usr/bin/env python3
"""Generate sample log entries for the dashboard. Run from log-management-ui/backend/."""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

try:
    from faker import Faker
    fake = Faker()
except ImportError:
    fake = None

LOG_FILE = Path(__file__).parent / "data" / "demo_logs.json"
LEVELS = ["INFO", "WARN", "ERROR", "DEBUG"]
SERVICES = ["api", "worker", "auth", "db", "cache", "nginx"]


def make_log(i: int) -> dict:
    ts = datetime.utcnow() - timedelta(hours=24 - i % 24, minutes=i % 60)
    level = LEVELS[i % len(LEVELS)]
    service = SERVICES[i % len(SERVICES)]
    if fake:
        msg = fake.sentence() if i % 3 else fake.catch_phrase()
    else:
        msg = f"Sample log message {i}: {level} from {service}"
    return {
        "id": i + 1,
        "timestamp": ts.isoformat() + "Z",
        "level": level,
        "service": service,
        "message": msg,
        "content": f"[{ts.strftime('%H:%M:%S')}] [{level}] [{service}] {msg}",
    }


def main():
    count = 50
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logs = [make_log(i) for i in range(count)]
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)
    print(f"Generated {count} log entries -> {LOG_FILE}")


if __name__ == "__main__":
    main()
