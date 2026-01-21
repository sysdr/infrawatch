import pytest
import asyncio
from backend.services.docker_client import DockerMonitorService

@pytest.mark.asyncio
async def test_get_containers():
    """Test getting container list"""
    service = DockerMonitorService()
    containers = await service.get_containers(all=True)
    assert isinstance(containers, list)

@pytest.mark.asyncio
async def test_container_stats():
    """Test getting container stats"""
    service = DockerMonitorService()
    containers = await service.get_containers(all=False)
    
    if containers:
        container_id = containers[0].id
        stats = await service.get_container_stats(container_id)
        
        if stats:  # Only if container is running
            assert stats.cpu_percent >= 0
            assert stats.memory_percent >= 0
            assert stats.container_id == container_id

@pytest.mark.asyncio
async def test_container_health():
    """Test getting container health"""
    service = DockerMonitorService()
    containers = await service.get_containers(all=False)
    
    if containers:
        container_id = containers[0].id
        health = await service.get_container_health(container_id)
        assert health is not None
        assert health.status in ['healthy', 'unhealthy', 'starting', 'none']
