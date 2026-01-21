import asyncio
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
from typing import Dict, List, Optional
import logging
from datetime import datetime
from app.core.database import AsyncSessionLocal
from models.k8s_models import Pod, Service, Deployment, Node, ClusterHealth, ResourceMetrics
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class K8sMonitorService:
    def __init__(self, ws_manager):
        self.ws_manager = ws_manager
        self.running = False
        self.watchers = {}
        self.v1_api = None
        self.apps_v1_api = None
        self.metrics_api = None
        
    async def initialize_k8s_client(self):
        """Initialize Kubernetes client"""
        try:
            # Try in-cluster config first, then fall back to kubeconfig
            try:
                config.load_incluster_config()
                logger.info("Loaded in-cluster Kubernetes configuration")
            except config.ConfigException:
                config.load_kube_config()
                logger.info("Loaded kubeconfig configuration")
            
            self.v1_api = client.CoreV1Api()
            self.apps_v1_api = client.AppsV1Api()
            
            # Test connection
            await asyncio.to_thread(self.v1_api.get_api_resources)
            logger.info("Successfully connected to Kubernetes API")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes client: {e}")
            return False
    
    async def start_monitoring(self):
        """Start all monitoring tasks"""
        self.running = True
        
        if not await self.initialize_k8s_client():
            logger.error("Cannot start monitoring without K8s connection")
            return
        
        # Start concurrent monitoring tasks
        tasks = [
            self.watch_pods(),
            self.watch_services(),
            self.watch_deployments(),
            self.watch_nodes(),
            self.collect_metrics(),
            self.calculate_health()
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop_monitoring(self):
        """Stop all monitoring"""
        self.running = False
        for watcher in self.watchers.values():
            if watcher:
                watcher.stop()
    
    async def watch_pods(self):
        """Watch pod changes in real-time"""
        logger.info("Starting pod watcher...")
        
        while self.running:
            try:
                w = watch.Watch()
                for event in w.stream(self.v1_api.list_pod_for_all_namespaces, timeout_seconds=300):
                    if not self.running:
                        break
                    
                    pod = event['object']
                    event_type = event['type']
                    
                    await self.process_pod_event(pod, event_type)
                    
            except ApiException as e:
                logger.error(f"Pod watch error: {e}")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Unexpected error in pod watcher: {e}")
                await asyncio.sleep(5)
    
    async def process_pod_event(self, pod, event_type):
        """Process pod events and store in database"""
        try:
            async with AsyncSessionLocal() as session:
                pod_data = {
                    'name': pod.metadata.name,
                    'namespace': pod.metadata.namespace,
                    'uid': pod.metadata.uid,
                    'status': pod.status.phase,
                    'node_name': pod.spec.node_name,
                    'ip': pod.status.pod_ip,
                    'labels': pod.metadata.labels or {},
                    'restart_count': sum(c.restart_count for c in (pod.status.container_statuses or [])),
                    'updated_at': datetime.utcnow()
                }
                
                # Upsert pod
                stmt = insert(Pod).values(**pod_data)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['uid'],
                    set_=pod_data
                )
                await session.execute(stmt)
                await session.commit()
                
                # Broadcast update via WebSocket
                await self.ws_manager.broadcast({
                    'type': 'pod_update',
                    'event': event_type,
                    'data': pod_data
                })
                
        except Exception as e:
            logger.error(f"Error processing pod event: {e}")
    
    async def watch_services(self):
        """Watch service changes"""
        logger.info("Starting service watcher...")
        
        while self.running:
            try:
                w = watch.Watch()
                for event in w.stream(self.v1_api.list_service_for_all_namespaces, timeout_seconds=300):
                    if not self.running:
                        break
                    
                    svc = event['object']
                    event_type = event['type']
                    
                    await self.process_service_event(svc, event_type)
                    
            except ApiException as e:
                logger.error(f"Service watch error: {e}")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Unexpected error in service watcher: {e}")
                await asyncio.sleep(5)
    
    async def process_service_event(self, svc, event_type):
        """Process service events"""
        try:
            async with AsyncSessionLocal() as session:
                ports = []
                for port in (svc.spec.ports or []):
                    ports.append({
                        'port': port.port,
                        'protocol': port.protocol,
                        'targetPort': str(port.target_port) if port.target_port else None
                    })
                
                svc_data = {
                    'name': svc.metadata.name,
                    'namespace': svc.metadata.namespace,
                    'uid': svc.metadata.uid,
                    'type': svc.spec.type,
                    'cluster_ip': svc.spec.cluster_ip,
                    'external_ip': svc.status.load_balancer.ingress[0].ip if svc.status.load_balancer.ingress else None,
                    'ports': ports,
                    'selector': svc.spec.selector or {},
                    'updated_at': datetime.utcnow()
                }
                
                stmt = insert(Service).values(**svc_data)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['uid'],
                    set_=svc_data
                )
                await session.execute(stmt)
                await session.commit()
                
                await self.ws_manager.broadcast({
                    'type': 'service_update',
                    'event': event_type,
                    'data': svc_data
                })
                
        except Exception as e:
            logger.error(f"Error processing service event: {e}")
    
    async def watch_deployments(self):
        """Watch deployment changes"""
        logger.info("Starting deployment watcher...")
        
        while self.running:
            try:
                w = watch.Watch()
                for event in w.stream(self.apps_v1_api.list_deployment_for_all_namespaces, timeout_seconds=300):
                    if not self.running:
                        break
                    
                    deploy = event['object']
                    event_type = event['type']
                    
                    await self.process_deployment_event(deploy, event_type)
                    
            except ApiException as e:
                logger.error(f"Deployment watch error: {e}")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Unexpected error in deployment watcher: {e}")
                await asyncio.sleep(5)
    
    async def process_deployment_event(self, deploy, event_type):
        """Process deployment events"""
        try:
            async with AsyncSessionLocal() as session:
                # Get first container image
                image = deploy.spec.template.spec.containers[0].image if deploy.spec.template.spec.containers else ""
                
                deploy_data = {
                    'name': deploy.metadata.name,
                    'namespace': deploy.metadata.namespace,
                    'uid': deploy.metadata.uid,
                    'replicas': deploy.spec.replicas,
                    'ready_replicas': deploy.status.ready_replicas or 0,
                    'available_replicas': deploy.status.available_replicas or 0,
                    'strategy': deploy.spec.strategy.type if deploy.spec.strategy else 'RollingUpdate',
                    'image': image,
                    'labels': deploy.metadata.labels or {},
                    'updated_at': datetime.utcnow()
                }
                
                stmt = insert(Deployment).values(**deploy_data)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['uid'],
                    set_=deploy_data
                )
                await session.execute(stmt)
                await session.commit()
                
                await self.ws_manager.broadcast({
                    'type': 'deployment_update',
                    'event': event_type,
                    'data': deploy_data
                })
                
        except Exception as e:
            logger.error(f"Error processing deployment event: {e}")
    
    async def watch_nodes(self):
        """Watch node changes"""
        logger.info("Starting node watcher...")
        
        while self.running:
            try:
                w = watch.Watch()
                for event in w.stream(self.v1_api.list_node, timeout_seconds=300):
                    if not self.running:
                        break
                    
                    node = event['object']
                    event_type = event['type']
                    
                    await self.process_node_event(node, event_type)
                    
            except ApiException as e:
                logger.error(f"Node watch error: {e}")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Unexpected error in node watcher: {e}")
                await asyncio.sleep(5)
    
    async def process_node_event(self, node, event_type):
        """Process node events"""
        try:
            async with AsyncSessionLocal() as session:
                # Determine node status
                status = "NotReady"
                for condition in (node.status.conditions or []):
                    if condition.type == "Ready":
                        status = "Ready" if condition.status == "True" else "NotReady"
                        break
                
                # Parse roles
                roles = []
                for label, value in (node.metadata.labels or {}).items():
                    if label.startswith("node-role.kubernetes.io/"):
                        roles.append(label.split("/")[1])
                
                # Parse capacity
                capacity_cpu = float(node.status.capacity.get('cpu', '0').rstrip('m')) / 1000
                capacity_memory = float(node.status.capacity.get('memory', '0Ki').rstrip('Ki')) / 1024 / 1024
                allocatable_cpu = float(node.status.allocatable.get('cpu', '0').rstrip('m')) / 1000
                allocatable_memory = float(node.status.allocatable.get('memory', '0Ki').rstrip('Ki')) / 1024 / 1024
                
                node_data = {
                    'name': node.metadata.name,
                    'uid': node.metadata.uid,
                    'status': status,
                    'roles': roles,
                    'capacity_cpu': capacity_cpu,
                    'capacity_memory': capacity_memory,
                    'allocatable_cpu': allocatable_cpu,
                    'allocatable_memory': allocatable_memory,
                    'os_image': node.status.node_info.os_image,
                    'kernel_version': node.status.node_info.kernel_version,
                    'container_runtime': node.status.node_info.container_runtime_version,
                    'updated_at': datetime.utcnow()
                }
                
                stmt = insert(Node).values(**node_data)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['uid'],
                    set_=node_data
                )
                await session.execute(stmt)
                await session.commit()
                
                await self.ws_manager.broadcast({
                    'type': 'node_update',
                    'event': event_type,
                    'data': node_data
                })
                
        except Exception as e:
            logger.error(f"Error processing node event: {e}")
    
    async def collect_metrics(self):
        """Collect resource metrics periodically"""
        logger.info("Starting metrics collector...")
        
        while self.running:
            try:
                # This is a simplified version - in production, use metrics-server API
                # For now, we'll simulate metrics collection
                await asyncio.sleep(15)
                
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(15)
    
    async def calculate_health(self):
        """Calculate cluster health score periodically"""
        logger.info("Starting health calculator...")
        
        while self.running:
            try:
                async with AsyncSessionLocal() as session:
                    # Get node stats
                    node_result = await session.execute(select(Node))
                    nodes = node_result.scalars().all()
                    total_nodes = len(nodes)
                    ready_nodes = sum(1 for n in nodes if n.status == "Ready")
                    
                    # Get pod stats
                    pod_result = await session.execute(select(Pod))
                    pods = pod_result.scalars().all()
                    total_pods = len(pods)
                    running_pods = sum(1 for p in pods if p.status == "Running")
                    failed_pods = sum(1 for p in pods if p.status == "Failed")
                    pending_pods = sum(1 for p in pods if p.status == "Pending")
                    
                    # Calculate component scores
                    node_health = (ready_nodes / total_nodes * 100) if total_nodes > 0 else 0
                    pod_health = (running_pods / total_pods * 100) if total_pods > 0 else 0
                    resource_health = 85.0  # Placeholder - would calculate from metrics
                    deployment_health = 90.0  # Placeholder - would calculate from deployments
                    api_latency = 95.0  # Placeholder - would measure API latency
                    
                    # Weighted overall score
                    overall = (
                        node_health * 0.30 +
                        pod_health * 0.25 +
                        resource_health * 0.20 +
                        deployment_health * 0.15 +
                        api_latency * 0.10
                    )
                    
                    # Store health record
                    health = ClusterHealth(
                        overall_score=overall,
                        node_health_score=node_health,
                        pod_health_score=pod_health,
                        resource_health_score=resource_health,
                        deployment_health_score=deployment_health,
                        api_latency_score=api_latency,
                        total_nodes=total_nodes,
                        ready_nodes=ready_nodes,
                        total_pods=total_pods,
                        running_pods=running_pods,
                        failed_pods=failed_pods,
                        pending_pods=pending_pods
                    )
                    session.add(health)
                    await session.commit()
                    
                    # Broadcast health update
                    await self.ws_manager.broadcast({
                        'type': 'health_update',
                        'data': {
                            'overall_score': overall,
                            'node_health': node_health,
                            'pod_health': pod_health,
                            'total_nodes': total_nodes,
                            'ready_nodes': ready_nodes,
                            'total_pods': total_pods,
                            'running_pods': running_pods,
                            'failed_pods': failed_pods,
                            'pending_pods': pending_pods
                        }
                    })
                
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error calculating health: {e}")
                await asyncio.sleep(5)
