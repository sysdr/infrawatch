import asyncio
import time
import gzip
import json
from typing import Dict, Set, Any, List
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

class StreamManager:
    def __init__(self, sio):
        self.sio = sio
        self.connections: Dict[str, Dict] = {}
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)
        self.message_queue: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.rate_limits: Dict[str, Dict] = defaultdict(lambda: {
            'count': 0,
            'window_start': time.time(),
            'max_per_second': 100
        })
        self.running = False
        
    async def handle_connect(self, sid: str):
        self.connections[sid] = {
            'connected_at': time.time(),
            'last_activity': time.time(),
            'messages_sent': 0,
            'compression_enabled': True,
            'throttle_level': 'normal'  # normal, reduced, minimal
        }
        await self.sio.emit('connection_established', {
            'sid': sid,
            'timestamp': time.time(),
            'compression': True
        }, room=sid)
        
    async def handle_disconnect(self, sid: str):
        if sid in self.connections:
            del self.connections[sid]
        for topic in list(self.subscriptions.keys()):
            self.subscriptions[topic].discard(sid)
        if sid in self.message_queue:
            del self.message_queue[sid]
            
    async def subscribe(self, sid: str, data: Dict):
        topics = data.get('topics', [])
        for topic in topics:
            self.subscriptions[topic].add(sid)
        await self.sio.emit('subscribed', {'topics': topics}, room=sid)
        
    async def unsubscribe(self, sid: str, data: Dict):
        topics = data.get('topics', [])
        for topic in topics:
            self.subscriptions[topic].discard(sid)
        await self.sio.emit('unsubscribed', {'topics': topics}, room=sid)
        
    async def broadcast(self, topic: str, data: Dict, priority: str = 'normal'):
        """Broadcast to all subscribers of a topic with throttling"""
        if topic not in self.subscriptions:
            logger.warning(f"No subscribers for topic '{topic}'")
            return
            
        subscribers = self.subscriptions[topic].copy()
        logger.info(f"Broadcasting to {len(subscribers)} subscriber(s) on topic '{topic}'")
        
        for sid in subscribers:
            if sid not in self.connections:
                continue
                
            if priority == 'critical':
                # Critical messages bypass throttling
                await self._send_message(sid, topic, data, compress=False)
            else:
                # Queue for throttled delivery
                self.message_queue[sid].append({
                    'topic': topic,
                    'data': data,
                    'timestamp': time.time(),
                    'priority': priority
                })
                
    async def _send_message(self, sid: str, topic: str, data: Dict, compress: bool = True):
        """Send message to specific client with optional compression"""
        try:
            if compress and self.connections[sid]['compression_enabled']:
                # Compress large payloads
                json_data = json.dumps(data)
                if len(json_data) > 1024:
                    compressed = gzip.compress(json_data.encode())
                    await self.sio.emit('compressed_message', {
                        'topic': topic,
                        'data': compressed.hex()
                    }, room=sid)
                    logger.info(f"Sent compressed message to {sid} on topic '{topic}'")
                    return
                    
            await self.sio.emit(topic, data, room=sid)
            logger.info(f"Sent message to {sid} on topic '{topic}'")
            self.connections[sid]['messages_sent'] += 1
            self.connections[sid]['last_activity'] = time.time()
            
        except Exception as e:
            logger.error(f"Error sending message to {sid}: {e}")
            
    async def start_throttling(self):
        """Background task for throttled message delivery"""
        self.running = True
        while self.running:
            await asyncio.sleep(0.1)  # Process every 100ms
            
            for sid in list(self.connections.keys()):
                if sid not in self.message_queue or not self.message_queue[sid]:
                    continue
                    
                # Check rate limit
                rate_info = self.rate_limits[sid]
                current_time = time.time()
                
                # Reset window if needed
                if current_time - rate_info['window_start'] >= 1.0:
                    rate_info['count'] = 0
                    rate_info['window_start'] = current_time
                    
                # Calculate how many messages we can send
                throttle_level = self.connections[sid]['throttle_level']
                max_batch = {
                    'normal': 10,
                    'reduced': 5,
                    'minimal': 2
                }.get(throttle_level, 10)
                
                # Process batch
                batch = []
                while len(batch) < max_batch and self.message_queue[sid]:
                    if rate_info['count'] >= rate_info['max_per_second']:
                        break
                    batch.append(self.message_queue[sid].popleft())
                    rate_info['count'] += 1
                    
                # Aggregate and send batch
                if batch:
                    await self._send_batch(sid, batch)
                    
    async def _send_batch(self, sid: str, messages: List[Dict]):
        """Send multiple messages as a batch"""
        if len(messages) == 1:
            msg = messages[0]
            await self._send_message(sid, msg['topic'], msg['data'])
        else:
            # Group by topic
            by_topic = defaultdict(list)
            for msg in messages:
                by_topic[msg['topic']].append(msg['data'])
                
            # Send aggregated batches
            for topic, data_list in by_topic.items():
                await self._send_message(sid, f"{topic}_batch", {
                    'items': data_list,
                    'count': len(data_list)
                })
                
    async def adjust_throttle(self, sid: str, level: str):
        """Dynamically adjust throttling level for a client"""
        if sid in self.connections:
            self.connections[sid]['throttle_level'] = level
            logger.info(f"Adjusted throttle for {sid} to {level}")
            
    async def stop(self):
        self.running = False
        
    def get_stats(self) -> Dict:
        """Get streaming statistics"""
        total_queued = sum(len(q) for q in self.message_queue.values())
        return {
            'active_connections': len(self.connections),
            'total_subscriptions': sum(len(s) for s in self.subscriptions.values()),
            'queued_messages': total_queued,
            'topics': len(self.subscriptions)
        }
