import asyncio
from typing import Dict, Any, List
from datetime import datetime
import structlog
from app.services.circuit_breaker import CircuitBreaker
from app.services.notification_engine import NotificationEngine
from app.services.alert_dispatcher import AlertDispatcher
from app.services.state_manager import StateManager
from app.websocket.manager import WebSocketManager
from app.core.config import settings
from app.core.metrics import MetricsCollector

logger = structlog.get_logger()

class IntegrationHub:
    """Orchestrates all real-time components"""
    
    def __init__(self, ws_manager: WebSocketManager, metrics: MetricsCollector):
        self.ws_manager = ws_manager
        self.metrics = metrics
        
        # Initialize components
        self.notification_engine = NotificationEngine(metrics)
        self.alert_dispatcher = AlertDispatcher(metrics)
        self.state_manager = StateManager()
        
        # Circuit breakers for each service
        self.circuit_breakers = {
            "notifications": CircuitBreaker("notifications", settings.CB_FAILURE_THRESHOLD),
            "alerts": CircuitBreaker("alerts", settings.CB_FAILURE_THRESHOLD),
            "state_sync": CircuitBreaker("state_sync", settings.CB_FAILURE_THRESHOLD)
        }
        
        # Message queue for batching
        self.message_queue: asyncio.Queue = asyncio.Queue(maxsize=settings.MESSAGE_QUEUE_SIZE)
        self.running = False
        self.tasks: List[asyncio.Task] = []
    
    async def start(self):
        """Start all background processors"""
        self.running = True
        
        # Start batch processor
        self.tasks.append(asyncio.create_task(self._batch_processor()))
        
        # Start health monitor
        self.tasks.append(asyncio.create_task(self._health_monitor()))
        
        # Start state sync
        self.tasks.append(asyncio.create_task(self._state_sync_loop()))
        
        logger.info("Integration hub started")
    
    async def stop(self):
        """Stop all processors"""
        self.running = False
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        logger.info("Integration hub stopped")
    
    async def handle_client_message(self, client_id: str, data: Dict[str, Any]):
        """Handle incoming client messages"""
        start_time = datetime.now()
        
        try:
            message_type = data.get("type")
            
            if message_type == "ping":
                await self.ws_manager.send_to_client(client_id, {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
            
            elif message_type == "create_alert":
                await self._handle_create_alert(client_id, data)
            
            elif message_type == "send_notification":
                await self._handle_send_notification(client_id, data)
            
            elif message_type == "sync_state":
                await self._handle_state_sync(client_id, data)
            
            elif message_type == "get_status":
                await self._handle_get_status(client_id)
            
            # Track latency
            latency = (datetime.now() - start_time).total_seconds() * 1000
            self.metrics.record_latency("message_processing", latency)
            
        except Exception as e:
            logger.error("Error handling message", 
                        client_id=client_id, 
                        error=str(e))
            await self.ws_manager.send_to_client(client_id, {
                "type": "error",
                "message": "Failed to process message"
            })
    
    async def _handle_create_alert(self, client_id: str, data: Dict[str, Any]):
        """Create and dispatch alert"""
        cb = self.circuit_breakers["alerts"]
        
        try:
            # Try to dispatch alert even if circuit breaker is open (for demo purposes)
            # In production, you might want to queue it
            alert = await self.alert_dispatcher.dispatch_alert(
                data.get("alert_data", {})
            )
            
            # Record success for circuit breaker
            cb.record_success()
            
            # Send confirmation to the client that created it
            await self.ws_manager.send_to_client(client_id, {
                "type": "alert_created",
                "alert": alert
            })
            
            # Also broadcast to all connected clients
            await self.ws_manager.broadcast({
                "type": "alert_created",
                "alert": alert
            }, exclude=[client_id])  # Exclude sender to avoid duplicate
            
            self.metrics.increment_counter("alerts_created")
            
        except Exception as e:
            logger.error("Failed to create alert", error=str(e))
            cb.record_failure()
            # Send error to client
            await self.ws_manager.send_to_client(client_id, {
                "type": "error",
                "message": f"Failed to create alert: {str(e)}"
            })
    
    async def _handle_send_notification(self, client_id: str, data: Dict[str, Any]):
        """Send notification through engine"""
        cb = self.circuit_breakers["notifications"]
        
        if cb.is_open():
            logger.warning("Notification circuit breaker open, using fallback")
            # Fallback: store in state for retry
            await self.state_manager.queue_notification(data)
            return
        
        try:
            result = await cb.call(
                self.notification_engine.send_notification,
                data.get("notification_data", {})
            )
            
            await self.ws_manager.send_to_client(client_id, {
                "type": "notification_sent",
                "result": result
            })
            
            self.metrics.increment_counter("notifications_sent")
            
        except Exception as e:
            logger.error("Failed to send notification", error=str(e))
            cb.record_failure()
    
    async def _handle_state_sync(self, client_id: str, data: Dict[str, Any]):
        """Sync state after reconnection"""
        last_version = data.get("last_version", 0)
        
        try:
            # Get missed events
            delta = await self.state_manager.get_delta(client_id, last_version)
            
            await self.ws_manager.send_to_client(client_id, {
                "type": "state_sync",
                "delta": delta,
                "current_version": delta["version"]
            })
            
            self.metrics.increment_counter("state_syncs")
            
        except Exception as e:
            logger.error("State sync failed", error=str(e))
    
    async def _handle_get_status(self, client_id: str):
        """Return system status"""
        status = {
            "type": "status",
            "connections": self.ws_manager.get_connection_count(),
            "circuit_breakers": {
                name: cb.get_state() 
                for name, cb in self.circuit_breakers.items()
            },
            "metrics": self.metrics.get_summary(),
            "timestamp": datetime.now().isoformat()
        }
        
        await self.ws_manager.send_to_client(client_id, status)
    
    async def _batch_processor(self):
        """Process messages in batches for efficiency"""
        batch = []
        last_flush = datetime.now()
        
        while self.running:
            try:
                # Wait for message or timeout
                try:
                    message = await asyncio.wait_for(
                        self.message_queue.get(),
                        timeout=settings.WS_MESSAGE_BATCH_TIMEOUT
                    )
                    batch.append(message)
                except asyncio.TimeoutError:
                    pass
                
                # Flush batch if full or timeout
                should_flush = (
                    len(batch) >= settings.WS_MESSAGE_BATCH_SIZE or
                    (datetime.now() - last_flush).total_seconds() > settings.WS_MESSAGE_BATCH_TIMEOUT
                )
                
                if should_flush and batch:
                    await self._process_batch(batch)
                    batch.clear()
                    last_flush = datetime.now()
                    
            except Exception as e:
                logger.error("Batch processor error", error=str(e))
    
    async def _process_batch(self, batch: List):
        """Process a batch of messages"""
        for message_type, client_id, data in batch:
            try:
                if message_type == "alert":
                    await self._handle_create_alert(client_id, data)
                # Add other message types
            except Exception as e:
                logger.error("Batch message error", error=str(e))
    
    async def _health_monitor(self):
        """Monitor system health"""
        while self.running:
            try:
                # Check circuit breakers
                for name, cb in self.circuit_breakers.items():
                    state = cb.get_state()
                    if state == "OPEN":
                        logger.warning("Circuit breaker open", service=name)
                
                # Check connection count
                conn_count = self.ws_manager.get_connection_count()
                if conn_count > settings.WS_MAX_CONNECTIONS * 0.9:
                    logger.warning("High connection count", count=conn_count)
                
                # Check latency
                avg_latency = self.metrics.get_average_latency("message_processing")
                if avg_latency > settings.LATENCY_BUDGET_MS:
                    logger.warning("High latency detected", latency_ms=avg_latency)
                
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error("Health monitor error", error=str(e))
    
    async def _state_sync_loop(self):
        """Periodically sync state across connections"""
        while self.running:
            try:
                await asyncio.sleep(30)
                
                # Get current state version
                version = await self.state_manager.get_current_version()
                
                # Broadcast version to all clients
                await self.ws_manager.broadcast({
                    "type": "version_check",
                    "version": version
                })
                
            except Exception as e:
                logger.error("State sync loop error", error=str(e))
