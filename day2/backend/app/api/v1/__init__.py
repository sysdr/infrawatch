from flask import Blueprint, jsonify, request
from app.models.infrastructure import Server, InfrastructureCluster
from datetime import datetime, timedelta
import random

health_bp = Blueprint('health', __name__)
infrastructure_bp = Blueprint('infrastructure', __name__)

@health_bp.route('/health')
def health_check():
    """Health endpoint - critical for load balancers and monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'service': 'infrawatch-backend'
    })

@infrastructure_bp.route('/servers')
def get_servers():
    """Get all monitored servers - simulates real infrastructure data"""
    # In production, this would query your database
    mock_servers = [
        Server(
            id=f'server-{i}',
            hostname=f'web-{i}.example.com',
            ip_address=f'10.0.1.{i+10}',
            status=random.choice(['healthy', 'warning', 'critical']),
            cpu_usage=random.uniform(10, 90),
            memory_usage=random.uniform(20, 80),
            disk_usage=random.uniform(30, 70),
            last_heartbeat=datetime.utcnow() - timedelta(seconds=random.randint(0, 300))
        ) for i in range(5)
    ]
    
    return jsonify({
        'servers': [server.to_dict() for server in mock_servers],
        'total_count': len(mock_servers),
        'timestamp': datetime.utcnow().isoformat()
    })

@infrastructure_bp.route('/clusters')
def get_clusters():
    """Get infrastructure clusters overview"""
    # Simulate cluster data
    servers = [
        Server(f'node-{i}', f'k8s-node-{i}', f'10.0.2.{i+10}', 
               'healthy', 45.2, 60.1, 35.8, datetime.utcnow())
        for i in range(3)
    ]
    
    cluster = InfrastructureCluster('production-cluster', servers)
    
    return jsonify({
        'cluster_name': cluster.name,
        'total_servers': cluster.total_servers,
        'healthy_servers': cluster.healthy_servers,
        'servers': [server.to_dict() for server in cluster.servers]
    })
