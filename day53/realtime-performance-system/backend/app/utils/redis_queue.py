import redis.asyncio as redis
import json
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class RedisQueue:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub = None
        
    async def connect(self):
        """Connect to Redis"""
        if self.redis_client is None:
            self.redis_client = await redis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379"),
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Redis connected")
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis disconnected")
    
    async def enqueue(self, queue_name: str, message: dict, priority: str = "normal"):
        """Add message to queue based on priority"""
        if priority == "critical":
            queue_name = f"{queue_name}:critical"
        elif priority == "low":
            queue_name = f"{queue_name}:low"
        
        await self.redis_client.lpush(queue_name, json.dumps(message))
        logger.debug(f"Enqueued to {queue_name}: {message.get('id')}")
    
    async def dequeue(self, queue_name: str, timeout: int = 1):
        """Remove and return message from queue (blocking)"""
        # Try critical queue first
        result = await self.redis_client.brpop(f"{queue_name}:critical", timeout=0.1)
        if result:
            return json.loads(result[1])
        
        # Then normal queue
        result = await self.redis_client.brpop(queue_name, timeout=timeout)
        if result:
            return json.loads(result[1])
        
        # Finally low priority
        result = await self.redis_client.brpop(f"{queue_name}:low", timeout=0.1)
        if result:
            return json.loads(result[1])
        
        return None
    
    async def get_queue_depth(self, queue_name: str) -> int:
        """Get total messages in all priority queues"""
        critical = await self.redis_client.llen(f"{queue_name}:critical")
        normal = await self.redis_client.llen(queue_name)
        low = await self.redis_client.llen(f"{queue_name}:low")
        return critical + normal + low
    
    async def publish(self, channel: str, message: dict):
        """Publish message to channel for inter-server communication"""
        await self.redis_client.publish(channel, json.dumps(message))
    
    async def subscribe(self, channel: str):
        """Subscribe to channel"""
        if self.pubsub is None:
            self.pubsub = self.redis_client.pubsub()
        await self.pubsub.subscribe(channel)
        return self.pubsub

redis_queue = RedisQueue()
