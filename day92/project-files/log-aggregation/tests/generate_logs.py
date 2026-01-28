#!/usr/bin/env python3
"""Generate sample logs for testing"""

import os
import time
import random
import json
from datetime import datetime
from pathlib import Path

# Log formats
LOG_FORMATS = {
    'json': lambda: json.dumps({
        'timestamp': datetime.utcnow().isoformat(),
        'level': random.choice(['INFO', 'INFO', 'INFO', 'WARN', 'ERROR']),
        'service': random.choice(['api', 'web', 'worker', 'database']),
        'message': random.choice([
            'Request processed successfully',
            'User authenticated',
            'Database query executed',
            'Cache hit',
            'Request timeout',
            'Connection established'
        ]),
        'user_id': random.randint(1000, 9999),
        'duration_ms': random.randint(10, 500)
    }),
    'apache': lambda: f'{random.choice(["192.168.1.1", "10.0.0.5", "172.16.0.10"])} - - [{datetime.utcnow().strftime("%d/%b/%Y:%H:%M:%S +0000")}] "GET {random.choice(["/api/users", "/health", "/metrics", "/login"])} HTTP/1.1" {random.choice([200, 200, 200, 404, 500])} {random.randint(500, 5000)}',
    'plain': lambda: f'[{datetime.utcnow().isoformat()}] {random.choice(["INFO", "INFO", "WARN", "ERROR"])}: {random.choice(["Processing request", "User action completed", "System check passed", "Warning: high memory usage", "Error: connection failed"])}'
}

def generate_logs(log_dir: str, count: int = 100, format_type: str = 'json'):
    """Generate sample logs"""
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    services = ['api', 'web', 'worker', 'database']
    
    for service in services:
        log_file = log_dir / f"{service}.log"
        
        with open(log_file, 'a') as f:
            for _ in range(count // len(services)):
                log_line = LOG_FORMATS[format_type]()
                f.write(log_line + '\n')
                time.sleep(0.01)  # Simulate real-time logging
    
    print(f"Generated {count} logs in {log_dir}")

if __name__ == "__main__":
    import sys
    log_dir = sys.argv[1] if len(sys.argv) > 1 else "../data/logs"
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    format_type = sys.argv[3] if len(sys.argv) > 3 else 'json'
    
    generate_logs(log_dir, count, format_type)
