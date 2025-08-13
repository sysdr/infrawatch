from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.server import Server, ServerStatus
from app.websocket.manager import ConnectionManager
import asyncio
import random
import logging

logger = logging.getLogger(__name__)

class ServerService:
    def __init__(self, manager: ConnectionManager):
        self.manager = manager

    async def create_server(self, db: AsyncSession, server_data: dict) -> Server:
        server = Server(**server_data)
        db.add(server)
        await db.commit()
        await db.refresh(server)
        
        # Notify WebSocket clients
        await self.manager.send_server_created(server.to_dict())
        
        # Simulate server creation process
        asyncio.create_task(self._simulate_server_lifecycle(db, server.id))
        
        return server

    async def get_servers(self, db: AsyncSession) -> list[Server]:
        result = await db.execute(select(Server))
        return result.scalars().all()

    async def get_server(self, db: AsyncSession, server_id: int) -> Server:
        result = await db.execute(select(Server).where(Server.id == server_id))
        return result.scalar_one_or_none()

    async def update_server_status(self, db: AsyncSession, server_id: int, status: ServerStatus) -> Server:
        await db.execute(
            update(Server)
            .where(Server.id == server_id)
            .values(status=status)
        )
        await db.commit()
        
        # Get updated server
        updated_server = await self.get_server(db, server_id)
        if updated_server:
            await self.manager.send_server_update(updated_server.to_dict())
        
        return updated_server

    async def delete_server(self, db: AsyncSession, server_id: int) -> bool:
        result = await db.execute(delete(Server).where(Server.id == server_id))
        await db.commit()
        
        if result.rowcount > 0:
            await self.manager.send_server_deleted(server_id)
            return True
        return False

    async def _simulate_server_lifecycle(self, db: AsyncSession, server_id: int):
        """Simulate realistic server startup process"""
        try:
            # Creating -> Starting (2-5 seconds)
            await asyncio.sleep(random.uniform(2, 5))
            await self.update_server_status(db, server_id, ServerStatus.STARTING)
            
            # Starting -> Running (5-10 seconds)
            await asyncio.sleep(random.uniform(5, 10))
            
            # 10% chance of failure during startup
            if random.random() < 0.1:
                await self.update_server_status(db, server_id, ServerStatus.ERROR)
            else:
                await self.update_server_status(db, server_id, ServerStatus.RUNNING)
                
        except Exception as e:
            logger.error(f"Error in server lifecycle simulation: {e}")
            await self.update_server_status(db, server_id, ServerStatus.ERROR)
