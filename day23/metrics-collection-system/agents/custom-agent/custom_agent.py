#!/usr/bin/env python3
import asyncio
import websockets
import orjson
import time
import logging
import random
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomAgent:
    def __init__(self, agent_id: str, server_url: str = "ws://localhost:8000"):
        self.agent_id = agent_id
        self.server_url = f"{server_url}/ws/agent/{agent_id}"
        self.websocket = None
        self.running = False
        self.collection_interval = 3  # seconds
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

    async def collect_custom_metrics(self):
        """Collect custom application metrics"""
        try:
            # Simulate application metrics
            metrics = [
                {
                    "name": "app_response_time",
                    "value": round(random.uniform(50, 200), 2),
                    "unit": "ms",
                    "timestamp": time.time()
                },
                {
                    "name": "app_requests_per_second",
                    "value": random.randint(10, 100),
                    "unit": "req/s",
                    "timestamp": time.time()
                },
                {
                    "name": "app_error_rate",
                    "value": round(random.uniform(0, 5), 2),
                    "unit": "%",
                    "timestamp": time.time()
                },
                {
                    "name": "database_connections",
                    "value": random.randint(5, 25),
                    "unit": "count",
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
                
                # Main collection loop
                while self.running and not self.websocket.closed:
                    # Collect and send metrics
                    metrics = await self.collect_custom_metrics()
                    for metric in metrics:
                        await self.send_metric(metric)
                    
                    logger.info(f"Sent {len(metrics)} custom metrics (total: {self.metrics_sent})")
                    await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Agent error: {e}")
                await asyncio.sleep(5)

    def stop(self):
        """Stop the agent"""
        self.running = False
        if self.websocket:
            asyncio.create_task(self.websocket.close())

async def main():
    agent_id = sys.argv[1] if len(sys.argv) > 1 else "custom-agent-1"
    agent = CustomAgent(agent_id)
    
    try:
        await agent.run()
    except KeyboardInterrupt:
        logger.info("Agent stopped by user")
        agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
