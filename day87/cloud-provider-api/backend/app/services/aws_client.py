import boto3
from typing import Dict, List, Optional
import asyncio
from functools import lru_cache
from app.core.config import settings

class AWSClientPool:
    """Manages persistent AWS client connections"""
    
    def __init__(self):
        self._clients: Dict[str, Dict[str, any]] = {}
    
    def get_client(self, service: str, region: str = None):
        """Get or create AWS client for service and region"""
        region = region or settings.AWS_REGION
        key = f"{service}:{region}"
        
        if key not in self._clients:
            client_kwargs = {"region_name": region}
            
            if settings.AWS_ACCESS_KEY_ID:
                client_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                client_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
            
            self._clients[key] = boto3.client(service, **client_kwargs)
        
        return self._clients[key]
    
    async def execute_with_retry(self, func, max_retries: int = 3):
        """Execute AWS API call with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return await asyncio.get_event_loop().run_in_executor(None, func)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
    
    def close_all(self):
        """Close all client connections"""
        for client in self._clients.values():
            try:
                client.close()
            except:
                pass
        self._clients.clear()

# Global client pool instance
aws_client_pool = AWSClientPool()
