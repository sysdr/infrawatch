# Access Instructions

## WSL2 Networking Fix

If you're accessing from a Windows browser and getting "ERR_CONNECTION_REFUSED", use one of these methods:

### Method 1: Use WSL IP Address (Recommended)
1. Get your WSL IP address:
   ```bash
   hostname -I | awk '{print $1}'
   ```
   Example: `172.22.24.182`

2. Access the frontend using:
   - **Frontend**: http://172.22.24.182:3000
   - **Backend API**: http://172.22.24.182:8001

### Method 2: Use localhost (if WSL port forwarding is configured)
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001

### Method 3: Use 127.0.0.1
- **Frontend**: http://127.0.0.1:3000
- **Backend API**: http://127.0.0.1:8001

## Current WSL IP
Run this command to get your current IP:
```bash
hostname -I | awk '{print $1}'
```

## Verify Services
```bash
# Check if services are running
pgrep -af "uvicorn.*8001|react-scripts"

# Test backend
curl http://localhost:8001/

# Test frontend
curl http://localhost:3000/
```

## Restart Services
```bash
cd /home/sdr/git/infrawatch/day89/cloud-resource-management
./start.sh
```
