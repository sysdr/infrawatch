#!/usr/bin/env python3
import asyncio
import websockets
import orjson
import psutil
import time
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemAgent:
    def __init__(self, agent_id: str, server_url: str = "ws://localhost:8000"):
        self.agent_id = agent_id
        self.server_url = f"{server_url}/ws/agent/{agent_id}"
        self.websocket = None
        self.running = False
        self.collection_interval = 5  # seconds
        self.metrics_sent = 0

    async def connect(self):
        """Connect to the metrics collection engine"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            logger.info(f"Agent {self.agent_id} connected to {self.server_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    async def collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            net_io = psutil.net_io_counters()
            
            metrics = [
                {
                    "name": "cpu_usage",
                    "value": cpu_percent,
                    "unit": "%",
                    "timestamp": time.time()
                },
                {
                    "name": "memory_usage",
                    "value": memory.percent,
                    "unit": "%",
                    "timestamp": time.time()
                },
                {
                    "name": "disk_usage",
                    "value": round((disk.used / disk.total) * 100, 2),
                    "unit": "%",
                    "device": "/",
                    "timestamp": time.time()
                },
                {
                    "name": "network_bytes_sent",
                    "value": round(net_io.bytes_sent / (1024 * 1024), 2),
                    "unit": "MB",
                    "interface": "total",
                    "timestamp": time.time()
                }
            ]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            return []

    async def send_metric(self, metric_data):
        """Send metric to collection engine"""
        try:
            message = {
                "type": "metric",
                "payload": metric_data
            }
            
            await self.websocket.send(orjson.dumps(message).decode())
            self.metrics_sent += 1
            
        except Exception as e:
            logger.error(f"Failed to send metric: {e}")

    async def send_heartbeat(self):
        """Send heartbeat to maintain connection"""
        try:
            message = {
                "type": "heartbeat",
                "agent_id": self.agent_id,
                "timestamp": time.time()
            }
            
            await self.websocket.send(orjson.dumps(message).decode())
            
        except Exception as e:
            logger.error(f"Failed to send heartbeat: {e}")

    async def listen_for_messages(self):
        """Listen for messages from the server"""
        try:
            async for message in self.websocket:
                data = orjson.loads(message)
                
                if data.get("type") == "config":
                    self.collection_interval = data.get("collection_interval", 5)
                    logger.info(f"Updated collection interval to {self.collection_interval}s")
                    
                elif data.get("type") == "heartbeat_ack":
                    logger.debug("Heartbeat acknowledged")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("Connection closed by server")
        except Exception as e:
            logger.error(f"Error listening for messages: {e}")

    async def run(self):
        """Main agent loop"""
        self.running = True
        
        while self.running:
            try:
                if not self.websocket or self.websocket.closed:
                    logger.info("Attempting to connect...")
                    if not await self.connect():
                        await asyncio.sleep(5)
                        continue
                
                # Start listening for messages
                listen_task = asyncio.create_task(self.listen_for_messages())
                
                # Main collection loop
                last_heartbeat = time.time()
                
                while self.running and not self.websocket.closed:
                    # Collect and send metrics
                    metrics = await self.collect_system_metrics()
                    for metric in metrics:
                        await self.send_metric(metric)
                    
                    # Send heartbeat every 30 seconds
                    if time.time() - last_heartbeat > 30:
                        await self.send_heartbeat()
                        last_heartbeat = time.time()
                    
                    logger.info(f"Sent {len(metrics)} metrics (total: {self.metrics_sent})")
                    await asyncio.sleep(self.collection_interval)
                
                listen_task.cancel()
                
            except Exception as e:
                logger.error(f"Agent error: {e}")
                await asyncio.sleep(5)

    def stop(self):
        """Stop the agent"""
        self.running = False
        if self.websocket:
            asyncio.create_task(self.websocket.close())

async def main():
    agent_id = sys.argv[1] if len(sys.argv) > 1 else "system-agent-1"
    agent = SystemAgent(agent_id)
    
    try:
        await agent.run()
    except KeyboardInterrupt:
        logger.info("Agent stopped by user")
        agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
