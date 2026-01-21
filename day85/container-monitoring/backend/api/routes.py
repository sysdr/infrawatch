from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import List
import asyncio
import logging
from ..models.container import (
    ContainerInfo, ContainerMetrics, ContainerHealth, 
    ContainerEvent, Alert, MetricsQuery
)
from ..services.docker_client import DockerMonitorService
from ..services.metrics_collector import MetricsCollector
from ..services.alert_manager import AlertManager

logger = logging.getLogger(__name__)

router = APIRouter()

# Global services
docker_service = None
try:
    docker_service = DockerMonitorService()
except Exception as e:
    logger.warning(f"Failed to initialize Docker service: {e}. Some features may not work.")
    docker_service = None

metrics_collector = MetricsCollector()
alert_manager = AlertManager()


def _serialize_baseline(baseline: dict | None) -> dict | None:
    """Convert baseline dict to JSON-serializable form."""
    if not baseline:
        return None
    serialized = dict(baseline)
    updated_at = serialized.get("updated_at")
    if updated_at:
        serialized["updated_at"] = updated_at.isoformat()
    return serialized

# Demo data generator for when Docker is not available
def generate_demo_containers():
    """Generate demo container data for testing"""
    from datetime import datetime, timedelta
    import random
    from ..models.container import ContainerInfo, ContainerMetrics, ContainerHealth
    
    demo_containers = []
    demo_names = ["web-server", "database", "redis-cache", "api-gateway", "worker-1"]
    
    for i, name in enumerate(demo_names):
        container_id = f"demo{i:012d}"
        demo_containers.append(ContainerInfo(
            id=container_id,
            name=name,
            image=f"{name}:latest",
            status="running",
            state="running",
            created=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            started_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24))
        ))
    
    return demo_containers

def generate_demo_metrics(container_id: str, container_name: str):
    """Generate demo metrics for a container"""
    from datetime import datetime
    import random
    from ..models.container import ContainerMetrics
    
    # Generate realistic-looking metrics
    cpu_percent = random.uniform(10, 80)
    memory_percent = random.uniform(20, 70)
    
    return ContainerMetrics(
        container_id=container_id,
        container_name=container_name,
        timestamp=datetime.utcnow(),
        cpu_percent=cpu_percent,
        cpu_delta=random.randint(1000000, 5000000),
        system_cpu_delta=random.randint(10000000, 50000000),
        memory_usage=random.randint(100000000, 500000000),
        memory_limit=1000000000,
        memory_percent=memory_percent,
        memory_cache=random.randint(10000000, 50000000),
        network_rx_bytes=random.randint(1000000, 10000000),
        network_tx_bytes=random.randint(500000, 5000000),
        network_rx_packets=random.randint(1000, 10000),
        network_tx_packets=random.randint(500, 5000),
        blkio_read=random.randint(100000, 1000000),
        blkio_write=random.randint(50000, 500000),
        pids_current=random.randint(5, 50)
    )

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()


@router.get("/containers", response_model=List[ContainerInfo])
async def get_containers(all: bool = False):
    """Get list of containers"""
    if docker_service:
        try:
            return await docker_service.get_containers(all=all)
        except Exception as e:
            logger.error(f"Error getting containers: {e}")
            # Fall through to demo data
    
    # Return demo data if Docker is not available
    return generate_demo_containers()


@router.get("/containers/{container_id}/metrics", response_model=ContainerMetrics)
async def get_container_metrics(container_id: str):
    """Get current metrics for a container"""
    metrics = await docker_service.get_container_stats(container_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Container not found")
    return metrics


@router.get("/containers/{container_id}/health", response_model=ContainerHealth)
async def get_container_health(container_id: str):
    """Get health status for a container"""
    health = await docker_service.get_container_health(container_id)
    if not health:
        raise HTTPException(status_code=404, detail="Container not found")
    return health


@router.get("/containers/{container_id}/history")
async def get_metrics_history(container_id: str, duration: int = 60):
    """Get metrics history for a container"""
    history = metrics_collector.get_metrics_history(container_id, duration)
    return {
        "container_id": container_id,
        "duration_seconds": duration,
        "data_points": len(history),
        "metrics": [m.model_dump() for m in history]
    }


@router.get("/alerts", response_model=List[Alert])
async def get_alerts(container_id: str = None):
    """Get active alerts"""
    return alert_manager.get_active_alerts(container_id)


@router.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics"""
    await manager.connect(websocket)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "Metrics WebSocket connected"
        })
        
        # Start metrics collection task
        collection_task = None
        
        async def collect_and_broadcast():
            while True:
                try:
                    containers = []
                    if docker_service:
                        try:
                            containers = await docker_service.get_containers(all=False)
                        except Exception as e:
                            logger.warning(f"Docker service error: {e}, using demo data")
                            containers = generate_demo_containers()
                    else:
                        # Use demo data when Docker is not available
                        containers = generate_demo_containers()
                    
                    if not containers:
                        # Send empty state message so client knows connection is working
                        await websocket.send_json({
                            "type": "metrics",
                            "data": {
                                "containers_count": 0,
                                "message": "No containers running"
                            }
                        })
                    else:
                        for container in containers:
                            # Get metrics
                            metrics = None
                            if docker_service:
                                try:
                                    metrics = await docker_service.get_container_stats(container.id)
                                except:
                                    pass
                            
                            # Use demo metrics if Docker metrics unavailable
                            if not metrics:
                                metrics = generate_demo_metrics(container.id, container.name)
                            
                            if metrics:
                                metrics_collector.add_metrics(metrics)
                                
                                # Check for anomalies
                                alerts = metrics_collector.check_anomalies(metrics)
                                for alert in alerts:
                                    alert_manager.add_alert(alert)
                                
                                # Get health
                                health = None
                                if docker_service:
                                    try:
                                        health = await docker_service.get_container_health(container.id)
                                    except:
                                        pass
                                
                                # Generate demo health if not available
                                if not health:
                                    from ..models.container import ContainerHealth
                                    from datetime import datetime
                                    import random
                                    health_statuses = ["healthy", "healthy", "healthy", "starting", "none"]
                                    health = ContainerHealth(
                                        container_id=container.id,
                                        container_name=container.name,
                                        timestamp=datetime.utcnow(),
                                        status=random.choice(health_statuses),
                                        failing_streak=0
                                    )
                                
                                if health:
                                    health_alert = alert_manager.check_health_alert(health)
                                    if health_alert:
                                        alert_manager.add_alert(health_alert)
                                
                                # Send update to this specific connection
                                # Use model_dump with mode='json' to handle datetime serialization
                                await websocket.send_json({
                                    "type": "metrics",
                                    "data": {
                                        "container": container.model_dump(mode='json'),
                                        "metrics": metrics.model_dump(mode='json'),
                                        "health": health.model_dump(mode='json') if health else None,
                                        "baseline": _serialize_baseline(metrics_collector.get_baseline(container.id)),
                                        "alerts": [a.model_dump(mode='json') for a in alerts]
                                    }
                                })
                    
                    await asyncio.sleep(1)  # Update every second
                    
                except Exception as e:
                    logger.error(f"Error in metrics collection: {e}")
                    await asyncio.sleep(5)
        
        collection_task = asyncio.create_task(collect_and_broadcast())
        
        # Handle keepalive messages (non-blocking)
        async def handle_messages():
            while True:
                try:
                    # Use asyncio.wait_for to make this non-blocking
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                    # Echo back for keepalive
                    await websocket.send_json({"type": "pong", "data": data})
                except asyncio.TimeoutError:
                    # Send periodic ping to keep connection alive
                    await websocket.send_json({"type": "ping"})
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    break
        
        # Run both tasks concurrently
        message_task = asyncio.create_task(handle_messages())
        
        # Wait for either task to complete
        done, pending = await asyncio.wait(
            [collection_task, message_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel remaining tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            
    except WebSocketDisconnect:
        if collection_task:
            collection_task.cancel()
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if collection_task:
            collection_task.cancel()
        manager.disconnect(websocket)


@router.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    """WebSocket endpoint for Docker events"""
    await websocket.accept()
    
    try:
        if docker_service:
            async for event in docker_service.stream_events():
                # Track restarts
                restart_alert = alert_manager.track_restart(event)
                if restart_alert:
                    alert_manager.add_alert(restart_alert)
                
                await websocket.send_json({
                    "type": "event",
                    "data": event.model_dump(mode='json')
                })
        else:
            # Send demo events when Docker is not available
            from ..models.container import ContainerEvent
            from datetime import datetime
            import random
            import asyncio
            
            demo_actions = ["start", "stop", "restart", "create"]
            demo_containers = ["web-server", "database", "redis-cache", "api-gateway"]
            
            while True:
                await asyncio.sleep(random.uniform(2, 5))  # Random interval
                event = ContainerEvent(
                    container_id=f"demo{random.randint(0, 4):012d}",
                    container_name=random.choice(demo_containers),
                    timestamp=datetime.utcnow(),
                    action=random.choice(demo_actions),
                    status="running" if random.choice(demo_actions) == "start" else "stopped"
                )
                await websocket.send_json({
                    "type": "event",
                    "data": event.model_dump(mode='json')
                })
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Event stream error: {e}")
