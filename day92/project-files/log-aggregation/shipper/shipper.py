#!/usr/bin/env python3
"""
Log Shipper - Monitors log files and forwards to aggregation server
"""

import os
import sys
import time
import json
import asyncio
import aiohttp
import hashlib
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from collections import deque
from datetime import datetime

class LogShipper:
    def __init__(self, config_file: str = "config.json"):
        self.config = self.load_config(config_file)
        self.buffer = deque(maxlen=self.config.get('buffer_size', 10000))
        self.server_url = self.config.get('server_url', 'http://localhost:8000')
        self.batch_size = self.config.get('batch_size', 100)
        self.flush_interval = self.config.get('flush_interval', 5)
        self.file_positions = {}
        self.running = True
    
    def load_config(self, config_file: str) -> dict:
        """Load shipper configuration"""
        if os.path.exists(config_file):
            with open(config_file) as f:
                return json.load(f)
        return {
            'watch_paths': ['../data/logs'],
            'server_url': 'http://localhost:8000',
            'buffer_size': 10000,
            'batch_size': 100,
            'flush_interval': 5
        }
    
    def tail_file(self, file_path: str):
        """Tail a log file from last known position"""
        try:
            # Get last position
            position = self.file_positions.get(file_path, 0)
            
            with open(file_path, 'r') as f:
                # Seek to last position
                f.seek(position)
                
                # Read new lines
                for line in f:
                    line = line.strip()
                    if line:
                        self.buffer.append({
                            'message': line,
                            'source_file': file_path,
                            'timestamp': datetime.utcnow().isoformat()
                        })
                
                # Update position
                self.file_positions[file_path] = f.tell()
        except Exception as e:
            print(f"Error tailing {file_path}: {e}")
    
    async def flush_buffer(self):
        """Flush buffered logs to server"""
        if not self.buffer:
            return
        
        # Get batch
        batch = []
        while self.buffer and len(batch) < self.batch_size:
            batch.append(self.buffer.popleft())
        
        # Send to server
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.server_url}/api/logs/ingest/batch",
                    json=batch,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        print(f"Shipped {len(batch)} logs")
                    else:
                        # Put back in buffer on failure
                        for log in reversed(batch):
                            self.buffer.appendleft(log)
                        print(f"Failed to ship logs: {response.status}")
        except Exception as e:
            # Put back in buffer on error
            for log in reversed(batch):
                self.buffer.appendleft(log)
            print(f"Error shipping logs: {e}")
    
    async def run(self):
        """Main shipper loop"""
        print(f"Log Shipper started - watching {self.config['watch_paths']}")
        
        while self.running:
            # Tail all log files
            for watch_path in self.config['watch_paths']:
                watch_path = Path(watch_path)
                if watch_path.exists():
                    for log_file in watch_path.rglob("*.log"):
                        self.tail_file(str(log_file))
            
            # Flush buffer
            await self.flush_buffer()
            
            # Sleep
            await asyncio.sleep(self.flush_interval)

if __name__ == "__main__":
    shipper = LogShipper()
    asyncio.run(shipper.run())
