import asyncio
import orjson
import structlog
from fastapi import WebSocket
from typing import Dict, Any

logger = structlog.get_logger()

class AgentProtocol:
    def __init__(self):
        self.connected_agents = {}
        self.dashboard_connections = set()

    async def handle_agent_connection(self, websocket: WebSocket, agent_id: str, 
                                    ingester, validator):
        """Handle agent WebSocket connection and message processing"""
        self.connected_agents[agent_id] = {
            "websocket": websocket,
            "connected_at": asyncio.get_event_loop().time(),
            "metrics_sent": 0
        }
        
        try:
            # Send initial configuration
            await websocket.send_text(orjson.dumps({
                "type": "config",
                "agent_id": agent_id,
                "collection_interval": 5,  # seconds
                "enabled_metrics": ["cpu", "memory", "disk", "network"]
            }).decode())

            # Listen for messages
            while True:
                message = await websocket.receive_text()
                await self._process_agent_message(agent_id, message, ingester, validator)
                
        except Exception as e:
            logger.error(f"Agent {agent_id} connection error: {e}")
        finally:
            if agent_id in self.connected_agents:
                del self.connected_agents[agent_id]

    async def handle_dashboard_connection(self, websocket: WebSocket, ingester):
        """Handle dashboard WebSocket connection for real-time updates"""
        self.dashboard_connections.add(websocket)
        
        try:
            # Send initial stats
            await websocket.send_text(orjson.dumps({
                "type": "stats",
                "data": ingester.get_stats()
            }).decode())

            # Keep connection alive and send periodic updates
            while True:
                await asyncio.sleep(2)
                stats = ingester.get_stats()
                await websocket.send_text(orjson.dumps({
                    "type": "stats_update",
                    "data": stats
                }).decode())
                
        except Exception as e:
            logger.error(f"Dashboard connection error: {e}")
        finally:
            self.dashboard_connections.discard(websocket)

    async def _process_agent_message(self, agent_id: str, message: str, 
                                   ingester, validator):
        """Process incoming message from agent"""
        try:
            data = orjson.loads(message)
            
            if data.get("type") == "metric":
                # Validate metric data
                if await validator.validate_metric(data.get("payload", {})):
                    await ingester.ingest_metric(agent_id, data["payload"])
                    self.connected_agents[agent_id]["metrics_sent"] += 1
                else:
                    logger.warning(f"Invalid metric from {agent_id}: {data}")
                    
            elif data.get("type") == "heartbeat":
                # Respond to heartbeat
                await self.connected_agents[agent_id]["websocket"].send_text(
                    orjson.dumps({"type": "heartbeat_ack"}).decode()
                )
                
        except Exception as e:
            logger.error(f"Failed to process message from {agent_id}: {e}")

    def get_agent_stats(self) -> Dict[str, Any]:
        return {
            "connected_agents": len(self.connected_agents),
            "dashboard_connections": len(self.dashboard_connections),
            "agents": {
                agent_id: {
                    "metrics_sent": info["metrics_sent"],
                    "uptime": asyncio.get_event_loop().time() - info["connected_at"]
                }
                for agent_id, info in self.connected_agents.items()
            }
        }
