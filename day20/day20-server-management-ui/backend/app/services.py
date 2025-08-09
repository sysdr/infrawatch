from typing import List, Optional, Dict, Any
import asyncio
import random
from datetime import datetime, timedelta
import json

from .models import Server, ServerCreate, ServerUpdate, BulkAction, ServerStatus, ServerMetrics

class ServerService:
    def __init__(self):
        self.servers: Dict[str, Server] = {}
        
    async def initialize(self):
        """Initialize with sample data"""
        sample_servers = [
            ServerCreate(
                name="Web Server 1",
                hostname="web01.example.com",
                ip_address="192.168.1.10",
                server_type="web",
                tags=["production", "frontend"]
            ),
            ServerCreate(
                name="Database Master",
                hostname="db-master.example.com", 
                ip_address="192.168.1.20",
                server_type="database",
                tags=["production", "master"]
            ),
            ServerCreate(
                name="Redis Cache",
                hostname="redis01.example.com",
                ip_address="192.168.1.30", 
                server_type="cache",
                tags=["production", "cache"]
            )
        ]
        
        for server_data in sample_servers:
            server = await self.create_server(server_data)
            # Set random status and metrics for demo
            server.status = random.choice(list(ServerStatus))
            server.cpu_usage = random.uniform(10, 90)
            server.memory_usage = random.uniform(20, 80)
            server.disk_usage = random.uniform(30, 70)
            server.uptime = random.randint(100, 10000)
    
    async def get_all_servers(self, 
                            page: int = 1, 
                            page_size: int = 50,
                            search: Optional[str] = None,
                            status: Optional[ServerStatus] = None,
                            server_type: Optional[str] = None) -> List[Server]:
        """Get filtered and paginated servers"""
        servers = list(self.servers.values())
        
        # Apply filters
        if search:
            servers = [s for s in servers if search.lower() in s.name.lower() or 
                      search.lower() in s.hostname.lower()]
        
        if status:
            servers = [s for s in servers if s.status == status]
            
        if server_type:
            servers = [s for s in servers if s.server_type == server_type]
        
        # Sort by name
        servers.sort(key=lambda x: x.name)
        
        # Paginate
        start = (page - 1) * page_size
        end = start + page_size
        return servers[start:end]
    
    async def get_server(self, server_id: str) -> Optional[Server]:
        """Get server by ID"""
        return self.servers.get(server_id)
    
    async def create_server(self, server_data: ServerCreate) -> Server:
        """Create new server"""
        server = Server(**server_data.dict())
        server.status = ServerStatus.OFFLINE
        server.last_checked = datetime.now()
        self.servers[server.id] = server
        return server
    
    async def update_server(self, server_id: str, server_data: ServerUpdate) -> Optional[Server]:
        """Update existing server"""
        if server_id not in self.servers:
            return None
        
        server = self.servers[server_id]
        for field, value in server_data.dict(exclude_unset=True).items():
            setattr(server, field, value)
        
        server.updated_at = datetime.now()
        return server
    
    async def delete_server(self, server_id: str) -> bool:
        """Delete server"""
        if server_id in self.servers:
            del self.servers[server_id]
            return True
        return False
    
    async def bulk_action(self, bulk_action: BulkAction) -> Dict[str, Any]:
        """Execute bulk action on multiple servers"""
        results = {"success": [], "failed": []}
        
        for server_id in bulk_action.server_ids:
            try:
                if bulk_action.action == "delete":
                    if await self.delete_server(server_id):
                        results["success"].append(server_id)
                    else:
                        results["failed"].append(server_id)
                        
                elif bulk_action.action == "update_status":
                    new_status = bulk_action.parameters.get("status")
                    server = await self.update_server(server_id, 
                        ServerUpdate(status=ServerStatus(new_status)))
                    if server:
                        results["success"].append(server_id)
                    else:
                        results["failed"].append(server_id)
                        
                elif bulk_action.action == "restart":
                    server = self.servers.get(server_id)
                    if server:
                        server.status = ServerStatus.MAINTENANCE
                        server.uptime = 0
                        results["success"].append(server_id)
                    else:
                        results["failed"].append(server_id)
                        
            except Exception as e:
                results["failed"].append(server_id)
        
        return results
    
    async def check_server_status(self, server_id: str) -> Optional[ServerStatus]:
        """Simulate server status check"""
        server = self.servers.get(server_id)
        if not server:
            return None
        
        # Simulate random status changes
        if random.random() < 0.1:  # 10% chance of status change
            new_status = random.choice(list(ServerStatus))
            server.status = new_status
            server.last_checked = datetime.now()
            
            # Update metrics based on status
            if new_status == ServerStatus.HEALTHY:
                server.cpu_usage = random.uniform(10, 50)
                server.memory_usage = random.uniform(20, 60)
            elif new_status == ServerStatus.WARNING:
                server.cpu_usage = random.uniform(60, 80)
                server.memory_usage = random.uniform(70, 85)
            elif new_status == ServerStatus.CRITICAL:
                server.cpu_usage = random.uniform(85, 100)
                server.memory_usage = random.uniform(90, 100)
        
        return server.status
    
    async def get_metrics(self) -> ServerMetrics:
        """Get server metrics summary"""
        servers = list(self.servers.values())
        total = len(servers)
        
        status_counts = {
            ServerStatus.HEALTHY: len([s for s in servers if s.status == ServerStatus.HEALTHY]),
            ServerStatus.WARNING: len([s for s in servers if s.status == ServerStatus.WARNING]),
            ServerStatus.CRITICAL: len([s for s in servers if s.status == ServerStatus.CRITICAL]),
            ServerStatus.OFFLINE: len([s for s in servers if s.status == ServerStatus.OFFLINE])
        }
        
        type_counts = {}
        for server in servers:
            type_counts[server.server_type] = type_counts.get(server.server_type, 0) + 1
        
        return ServerMetrics(
            total_servers=total,
            healthy_count=status_counts[ServerStatus.HEALTHY],
            warning_count=status_counts[ServerStatus.WARNING], 
            critical_count=status_counts[ServerStatus.CRITICAL],
            offline_count=status_counts[ServerStatus.OFFLINE],
            server_types=type_counts
        )

# WebSocket Manager
class WebSocketManager:
    def __init__(self):
        self.active_connections: List = []
        self.rooms: Dict[str, List] = {}

    async def connect(self, websocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket):
        self.active_connections.remove(websocket)
        # Remove from all rooms
        for room_connections in self.rooms.values():
            if websocket in room_connections:
                room_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                # Remove failed connections
                self.active_connections.remove(connection)

    async def add_to_room(self, websocket, room: str):
        if room not in self.rooms:
            self.rooms[room] = []
        self.rooms[room].append(websocket)

websocket_manager = WebSocketManager()
