# Infrastructure Discovery System - Access Guide

## ✅ Services Status

Both services are running and accessible:

- **Backend API**: http://localhost:8000 (or http://127.0.0.1:8000)
- **Frontend Dashboard**: http://localhost:3001 (or http://127.0.0.1:3001)
- **API Documentation**: http://localhost:8000/docs

## 🔧 WSL2 Access Instructions

### If you're accessing from Windows Browser:

1. **Try localhost first** (should work with modern WSL2):
   - Frontend: http://localhost:3001
   - Backend: http://localhost:8000

2. **If localhost doesn't work**, use the WSL2 IP address:
   - Find your WSL2 IP: `hostname -I` (currently: 172.22.24.182)
   - Frontend: http://172.22.24.182:3001
   - Backend: http://172.22.24.182:8000

3. **Alternative - Use 127.0.0.1**:
   - Frontend: http://127.0.0.1:3001
   - Backend: http://127.0.0.1:8000

### If you're accessing from WSL2 terminal:

```bash
# Test backend
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3001
```

## 🚨 Troubleshooting ERR_CONNECTION_REFUSED

### 1. Check if services are running:
```bash
cd /home/sdr/git/infrawatch/day88/infrastructure-discovery
./scripts/stop.sh
./scripts/start.sh
```

### 2. Verify ports are listening:
```bash
lsof -Pi :3001 -sTCP:LISTEN  # Frontend
lsof -Pi :8000 -sTCP:LISTEN  # Backend
```

### 3. Check for port conflicts:
```bash
# Kill any conflicting processes
pkill -f "react-scripts start"
pkill -f "uvicorn app.main:app"
```

### 4. Restart services:
```bash
cd /home/sdr/git/infrawatch/day88/infrastructure-discovery
./scripts/stop.sh
sleep 3
./scripts/start.sh
```

### 5. Windows Firewall:
If using WSL2 IP address, ensure Windows Firewall allows connections on ports 3001 and 8000.

## 📊 Verify Dashboard Metrics

Once accessible, verify all metrics show non-zero values:

```bash
# Check inventory stats
curl http://localhost:8000/api/inventory/stats | python3 -m json.tool

# Trigger discovery scan
curl -X POST http://localhost:8000/api/discovery/scan | python3 -m json.tool

# Check topology
curl http://localhost:8000/api/topology/graph | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"Nodes: {len(d.get('nodes', []))}, Links: {len(d.get('links', []))}\")"
```

Expected results:
- Total Resources: 32
- Load Balancers: 4
- Instances: 20
- Databases: 5
- Security Groups: 3
- Topology: 32 nodes, 45 links

## 🔗 Quick Links

- **Frontend Dashboard**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

## 📝 Notes

- Frontend is configured with `HOST=0.0.0.0` for WSL2 compatibility
- Backend is configured with `--host 0.0.0.0` for WSL2 compatibility
- Both services bind to all interfaces, making them accessible from Windows
