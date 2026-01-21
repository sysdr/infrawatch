import docker
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, List, AsyncIterator
from docker.models.containers import Container
from ..models.container import ContainerMetrics, ContainerHealth, ContainerEvent, ContainerInfo

logger = logging.getLogger(__name__)


class DockerMonitorService:
    """Docker API client for container monitoring"""
    
    def __init__(self):
        self.client = docker.from_env()
        self._event_task: Optional[asyncio.Task] = None
        self._running = False
        
    async def get_containers(self, all: bool = False) -> List[ContainerInfo]:
        """Get list of containers"""
        try:
            containers = self.client.containers.list(all=all)
            return [self._parse_container_info(c) for c in containers]
        except Exception as e:
            logger.error(f"Error getting containers: {e}")
            return []
    
    async def get_container_stats(self, container_id: str) -> Optional[ContainerMetrics]:
        """Get real-time stats for a container"""
        try:
            container = self.client.containers.get(container_id)
            stats = container.stats(stream=False, decode=True)
            return self._parse_stats(container_id, container.name, stats)
        except docker.errors.NotFound:
            logger.warning(f"Container {container_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting stats for {container_id}: {e}")
            return None
    
    async def stream_container_stats(
        self, container_id: str
    ) -> AsyncIterator[ContainerMetrics]:
        """Stream real-time stats for a container"""
        try:
            container = self.client.containers.get(container_id)
            stats_stream = container.stats(stream=True, decode=True)
            
            for stats in stats_stream:
                if not self._running:
                    break
                metrics = self._parse_stats(container_id, container.name, stats)
                if metrics:
                    yield metrics
                await asyncio.sleep(0.1)  # Allow other coroutines to run
                
        except docker.errors.NotFound:
            logger.warning(f"Container {container_id} not found")
        except Exception as e:
            logger.error(f"Error streaming stats for {container_id}: {e}")
    
    async def get_container_health(self, container_id: str) -> Optional[ContainerHealth]:
        """Get container health status"""
        try:
            container = self.client.containers.get(container_id)
            container.reload()  # Refresh container state
            
            health_data = container.attrs.get('State', {}).get('Health', {})
            
            if not health_data:
                return ContainerHealth(
                    container_id=container_id,
                    container_name=container.name,
                    timestamp=datetime.utcnow(),
                    status="none",
                    failing_streak=0
                )
            
            return ContainerHealth(
                container_id=container_id,
                container_name=container.name,
                timestamp=datetime.utcnow(),
                status=health_data.get('Status', 'none'),
                failing_streak=health_data.get('FailingStreak', 0),
                log=health_data.get('Log', [{}])[-1].get('Output') if health_data.get('Log') else None,
                exit_code=health_data.get('Log', [{}])[-1].get('ExitCode') if health_data.get('Log') else None
            )
            
        except docker.errors.NotFound:
            return None
        except Exception as e:
            logger.error(f"Error getting health for {container_id}: {e}")
            return None
    
    async def stream_events(self) -> AsyncIterator[ContainerEvent]:
        """Stream Docker events"""
        self._running = True
        try:
            for event in self.client.events(decode=True):
                if not self._running:
                    break
                
                if event.get('Type') == 'container':
                    container_event = self._parse_event(event)
                    if container_event:
                        yield container_event
                        
                await asyncio.sleep(0.01)
                
        except Exception as e:
            logger.error(f"Error streaming events: {e}")
        finally:
            self._running = False
    
    def _parse_container_info(self, container: Container) -> ContainerInfo:
        """Parse container into ContainerInfo"""
        state = container.attrs.get('State', {})
        created = datetime.fromisoformat(container.attrs['Created'].replace('Z', '+00:00'))
        started_at = None
        
        if state.get('StartedAt'):
            try:
                started_at = datetime.fromisoformat(state['StartedAt'].replace('Z', '+00:00'))
            except:
                pass
        
        return ContainerInfo(
            id=container.id,
            name=container.name,
            image=container.image.tags[0] if container.image.tags else container.image.short_id,
            status=container.status,
            state=state.get('Status', 'unknown'),
            created=created,
            started_at=started_at
        )
    
    def _parse_stats(
        self, container_id: str, container_name: str, stats: Dict
    ) -> Optional[ContainerMetrics]:
        """Parse Docker stats into ContainerMetrics"""
        try:
            # CPU calculation
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_cpu_delta = stats['cpu_stats']['system_cpu_usage'] - \
                              stats['precpu_stats']['system_cpu_usage']
            
            cpu_percent = 0.0
            if system_cpu_delta > 0:
                num_cpus = len(stats['cpu_stats']['cpu_usage'].get('percpu_usage', [1]))
                cpu_percent = (cpu_delta / system_cpu_delta) * num_cpus * 100.0
            
            # Memory calculation
            memory_stats = stats['memory_stats']
            memory_usage = memory_stats['usage']
            memory_limit = memory_stats['limit']
            memory_cache = memory_stats.get('stats', {}).get('cache', 0)
            memory_percent = (memory_usage / memory_limit) * 100.0 if memory_limit > 0 else 0.0
            
            # Network calculation
            networks = stats.get('networks', {})
            network_rx = sum(net['rx_bytes'] for net in networks.values())
            network_tx = sum(net['tx_bytes'] for net in networks.values())
            network_rx_packets = sum(net['rx_packets'] for net in networks.values())
            network_tx_packets = sum(net['tx_packets'] for net in networks.values())
            
            # Block I/O calculation
            blkio_stats = stats.get('blkio_stats', {})
            blkio_read = sum(
                item['value'] for item in blkio_stats.get('io_service_bytes_recursive', [])
                if item['op'] == 'read'
            ) if blkio_stats.get('io_service_bytes_recursive') else 0
            
            blkio_write = sum(
                item['value'] for item in blkio_stats.get('io_service_bytes_recursive', [])
                if item['op'] == 'write'
            ) if blkio_stats.get('io_service_bytes_recursive') else 0
            
            # PIDs
            pids_current = stats.get('pids_stats', {}).get('current')
            
            return ContainerMetrics(
                container_id=container_id,
                container_name=container_name,
                timestamp=datetime.utcnow(),
                cpu_percent=min(cpu_percent, 100.0),
                cpu_delta=cpu_delta,
                system_cpu_delta=system_cpu_delta,
                memory_usage=memory_usage,
                memory_limit=memory_limit,
                memory_percent=min(memory_percent, 100.0),
                memory_cache=memory_cache,
                network_rx_bytes=network_rx,
                network_tx_bytes=network_tx,
                network_rx_packets=network_rx_packets,
                network_tx_packets=network_tx_packets,
                blkio_read=blkio_read,
                blkio_write=blkio_write,
                pids_current=pids_current
            )
            
        except Exception as e:
            logger.error(f"Error parsing stats: {e}")
            return None
    
    def _parse_event(self, event: Dict) -> Optional[ContainerEvent]:
        """Parse Docker event into ContainerEvent"""
        try:
            action = event.get('Action', '')
            attributes = event.get('Actor', {}).get('Attributes', {})
            
            return ContainerEvent(
                container_id=event['Actor']['ID'][:12],
                container_name=attributes.get('name', 'unknown'),
                timestamp=datetime.fromtimestamp(event['time']),
                action=action,
                status=event.get('status', ''),
                exit_code=int(attributes.get('exitCode')) if attributes.get('exitCode') else None,
                error=attributes.get('error'),
                attributes=attributes
            )
        except Exception as e:
            logger.error(f"Error parsing event: {e}")
            return None
    
    def stop(self):
        """Stop monitoring"""
        self._running = False
