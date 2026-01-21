# Day 86: Kubernetes Integration - Production Monitoring System

A production-ready Kubernetes monitoring system with real-time updates and comprehensive cluster visibility.

## Features

- Real-time pod, service, deployment, and node monitoring
- Cluster health scoring with component breakdown
- WebSocket-based live updates
- Professional dashboard UI inspired by Datadog
- PostgreSQL storage for metrics history
- Docker-based deployment

## Quick Start

### With Docker (Recommended)
```bash
docker-compose up --build
```

### Without Docker
```bash
./build.sh
# Follow the instructions printed by the build script
```

## Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Architecture

- Backend: FastAPI + Kubernetes Python Client
- Frontend: React + Material-UI
- Database: PostgreSQL 16
- Cache: Redis 7
- Deployment: Docker Compose

## Monitoring Capabilities

1. **Pod Monitoring**: Track status, restarts, resource usage
2. **Service Discovery**: Monitor ClusterIP, NodePort, LoadBalancer services
3. **Deployment Tracking**: Rollout status and replica health
4. **Node Health**: Capacity, allocatable resources, status
5. **Cluster Health**: Composite scoring across all components

## Testing

```bash
pytest tests/ -v
```

## Notes

- Requires access to a Kubernetes cluster (local or remote)
- Configure kubeconfig at ~/.kube/config
- For production use, implement proper authentication and RBAC
