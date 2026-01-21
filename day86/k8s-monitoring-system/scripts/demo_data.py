#!/usr/bin/env python3
"""
Demo data generator for K8s Monitoring System
Populates database with mock Kubernetes data for dashboard testing
"""

import asyncio
import sys
import os
from datetime import datetime

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.database import AsyncSessionLocal, init_db
from models.k8s_models import Pod, Service, Deployment, Node, ClusterHealth, ResourceMetrics
from sqlalchemy.dialects.postgresql import insert

async def create_demo_data():
    """Create demo Kubernetes data"""
    print("Initializing database...")
    await init_db()
    
    async with AsyncSessionLocal() as session:
        print("Creating demo nodes...")
        # Create demo nodes
        nodes_data = [
            {
                'name': 'node-1',
                'uid': 'node-1-uid',
                'status': 'Ready',
                'roles': ['master'],
                'capacity_cpu': 8.0,
                'capacity_memory': 32768.0,  # 32GB
                'allocatable_cpu': 7.5,
                'allocatable_memory': 30720.0,
                'os_image': 'Ubuntu 22.04.3 LTS',
                'kernel_version': '5.15.0',
                'container_runtime': 'containerd://1.7.0',
            },
            {
                'name': 'node-2',
                'uid': 'node-2-uid',
                'status': 'Ready',
                'roles': ['worker'],
                'capacity_cpu': 4.0,
                'capacity_memory': 16384.0,  # 16GB
                'allocatable_cpu': 3.8,
                'allocatable_memory': 15360.0,
                'os_image': 'Ubuntu 22.04.3 LTS',
                'kernel_version': '5.15.0',
                'container_runtime': 'containerd://1.7.0',
            },
            {
                'name': 'node-3',
                'uid': 'node-3-uid',
                'status': 'Ready',
                'roles': ['worker'],
                'capacity_cpu': 4.0,
                'capacity_memory': 16384.0,
                'allocatable_cpu': 3.7,
                'allocatable_memory': 15360.0,
                'os_image': 'Ubuntu 22.04.3 LTS',
                'kernel_version': '5.15.0',
                'container_runtime': 'containerd://1.7.0',
            },
        ]
        
        for node_data in nodes_data:
            stmt = insert(Node).values(**node_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['uid'],
                set_=node_data
            )
            await session.execute(stmt)
        
        print("Creating demo pods...")
        # Create demo pods
        pods_data = [
            {
                'name': 'nginx-deployment-7d8b4f9c5d-abc12',
                'namespace': 'default',
                'uid': 'pod-1-uid',
                'status': 'Running',
                'node_name': 'node-1',
                'ip': '10.244.1.5',
                'labels': {'app': 'nginx', 'version': '1.0'},
                'restart_count': 0,
            },
            {
                'name': 'nginx-deployment-7d8b4f9c5d-def34',
                'namespace': 'default',
                'uid': 'pod-2-uid',
                'status': 'Running',
                'node_name': 'node-2',
                'ip': '10.244.2.8',
                'labels': {'app': 'nginx', 'version': '1.0'},
                'restart_count': 0,
            },
            {
                'name': 'nginx-deployment-7d8b4f9c5d-ghi56',
                'namespace': 'default',
                'uid': 'pod-3-uid',
                'status': 'Running',
                'node_name': 'node-3',
                'ip': '10.244.3.12',
                'labels': {'app': 'nginx', 'version': '1.0'},
                'restart_count': 1,
            },
            {
                'name': 'redis-pod-xyz789',
                'namespace': 'default',
                'uid': 'pod-4-uid',
                'status': 'Running',
                'node_name': 'node-1',
                'ip': '10.244.1.15',
                'labels': {'app': 'redis'},
                'restart_count': 0,
            },
            {
                'name': 'api-pod-abc456',
                'namespace': 'production',
                'uid': 'pod-5-uid',
                'status': 'Running',
                'node_name': 'node-2',
                'ip': '10.244.2.20',
                'labels': {'app': 'api', 'env': 'prod'},
                'restart_count': 0,
            },
        ]
        
        for pod_data in pods_data:
            stmt = insert(Pod).values(**pod_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['uid'],
                set_=pod_data
            )
            await session.execute(stmt)
        
        print("Creating demo services...")
        # Create demo services
        services_data = [
            {
                'name': 'nginx-service',
                'namespace': 'default',
                'uid': 'svc-1-uid',
                'type': 'ClusterIP',
                'cluster_ip': '10.96.1.10',
                'external_ip': None,
                'ports': [{'port': 80, 'protocol': 'TCP', 'targetPort': '8080'}],
                'selector': {'app': 'nginx'},
            },
            {
                'name': 'redis-service',
                'namespace': 'default',
                'uid': 'svc-2-uid',
                'type': 'ClusterIP',
                'cluster_ip': '10.96.1.20',
                'external_ip': None,
                'ports': [{'port': 6379, 'protocol': 'TCP', 'targetPort': '6379'}],
                'selector': {'app': 'redis'},
            },
            {
                'name': 'api-service',
                'namespace': 'production',
                'uid': 'svc-3-uid',
                'type': 'LoadBalancer',
                'cluster_ip': '10.96.2.30',
                'external_ip': '192.168.1.100',
                'ports': [{'port': 443, 'protocol': 'TCP', 'targetPort': '8443'}],
                'selector': {'app': 'api'},
            },
        ]
        
        for svc_data in services_data:
            stmt = insert(Service).values(**svc_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['uid'],
                set_=svc_data
            )
            await session.execute(stmt)
        
        print("Creating demo deployments...")
        # Create demo deployments
        deployments_data = [
            {
                'name': 'nginx-deployment',
                'namespace': 'default',
                'uid': 'deploy-1-uid',
                'replicas': 3,
                'ready_replicas': 3,
                'available_replicas': 3,
                'strategy': 'RollingUpdate',
                'image': 'nginx:1.25',
                'labels': {'app': 'nginx'},
            },
            {
                'name': 'redis-deployment',
                'namespace': 'default',
                'uid': 'deploy-2-uid',
                'replicas': 1,
                'ready_replicas': 1,
                'available_replicas': 1,
                'strategy': 'Recreate',
                'image': 'redis:7-alpine',
                'labels': {'app': 'redis'},
            },
            {
                'name': 'api-deployment',
                'namespace': 'production',
                'uid': 'deploy-3-uid',
                'replicas': 2,
                'ready_replicas': 2,
                'available_replicas': 2,
                'strategy': 'RollingUpdate',
                'image': 'myapi:v1.2.3',
                'labels': {'app': 'api', 'env': 'prod'},
            },
        ]
        
        for deploy_data in deployments_data:
            stmt = insert(Deployment).values(**deploy_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['uid'],
                set_=deploy_data
            )
            await session.execute(stmt)
        
        print("Creating demo health records...")
        # Create demo health records
        health_data = ClusterHealth(
            overall_score=92.5,
            node_health_score=100.0,
            pod_health_score=100.0,
            resource_health_score=85.0,
            deployment_health_score=100.0,
            api_latency_score=95.0,
            total_nodes=3,
            ready_nodes=3,
            total_pods=5,
            running_pods=5,
            failed_pods=0,
            pending_pods=0
        )
        session.add(health_data)
        
        print("Creating demo metrics...")
        # Create demo resource metrics
        metrics_data = [
            {
                'resource_type': 'pod',
                'resource_name': 'nginx-deployment-7d8b4f9c5d-abc12',
                'namespace': 'default',
                'cpu_usage': 0.15,
                'memory_usage': 128.5,
                'cpu_limit': 0.5,
                'memory_limit': 512.0,
            },
            {
                'resource_type': 'pod',
                'resource_name': 'redis-pod-xyz789',
                'namespace': 'default',
                'cpu_usage': 0.08,
                'memory_usage': 256.0,
                'cpu_limit': 1.0,
                'memory_limit': 1024.0,
            },
            {
                'resource_type': 'node',
                'resource_name': 'node-1',
                'namespace': None,
                'cpu_usage': 2.5,
                'memory_usage': 8192.0,
                'cpu_limit': 8.0,
                'memory_limit': 32768.0,
            },
        ]
        
        for metric_data in metrics_data:
            session.add(ResourceMetrics(**metric_data))
        
        await session.commit()
        print("Demo data created successfully!")
        print("\nSummary:")
        print("  - Nodes: 3")
        print("  - Pods: 5")
        print("  - Services: 3")
        print("  - Deployments: 3")
        print("  - Health records: 1")
        print("  - Metrics: 3")

if __name__ == "__main__":
    asyncio.run(create_demo_data())
