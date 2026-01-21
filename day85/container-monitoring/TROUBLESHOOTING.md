# Troubleshooting Guide - Container Monitoring Dashboard

## Dashboard Shows "Disconnected"

### Quick Fix

1. **Check if backend is running:**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy","service":"container-monitoring"}`

2. **If backend is not running, start it:**
   ```bash
   cd container-monitoring/backend
   source venv/bin/activate
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Check frontend:**
   ```bash
   cd container-monitoring/frontend
   npm run dev
   ```

4. **Refresh browser:**
   - Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)

### Automated Check

Run the setup check script:
```bash
cd container-monitoring
./check_setup.sh
```

## Common Issues

### 1. "Disconnected" Status

**Symptoms:**
- Red "Disconnected" badge in top-right
- No containers showing
- Error message about connection

**Solutions:**
- Verify backend is running on port 8000
- Check browser console (F12) for WebSocket errors
- Verify CORS settings in backend
- Check firewall/network settings

### 2. "No containers running"

**Symptoms:**
- Shows "Connected" but "No containers running"

**Solutions:**
- This is normal if no Docker containers are running
- Start a test container:
  ```bash
  docker run -d --name test-nginx nginx
  ```
- Check containers: `docker ps`

### 3. WebSocket Connection Errors

**Symptoms:**
- Console shows WebSocket connection errors
- "Failed to connect to metrics stream"

**Solutions:**
- Verify backend WebSocket endpoint: `ws://localhost:8000/api/v1/ws/metrics`
- Check Vite proxy configuration in `vite.config.js`
- Verify backend allows WebSocket connections
- Check browser DevTools → Network → WS tab

### 4. Backend Not Starting

**Symptoms:**
- Backend fails to start
- Port 8000 already in use

**Solutions:**
- Check if port is in use: `lsof -i :8000` or `netstat -an | grep 8000`
- Kill process using port: `kill -9 $(lsof -t -i:8000)`
- Or change port in backend startup command

### 5. Frontend Not Starting

**Symptoms:**
- Frontend fails to start
- Port 3000 already in use

**Solutions:**
- Vite will automatically use next available port (3001, 3002, etc.)
- Check terminal output for actual port
- Or kill process: `kill -9 $(lsof -t -i:3000)`

### 6. Docker Permission Errors

**Symptoms:**
- Backend can't access Docker
- "Permission denied" errors

**Solutions:**
- Add user to docker group: `sudo usermod -aG docker $USER`
- Log out and back in
- Or use: `sudo chmod 666 /var/run/docker.sock` (less secure)

## Diagnostic Steps

### Step 1: Verify Backend
```bash
# Check backend health
curl http://localhost:8000/health

# Check API docs
curl http://localhost:8000/docs

# Check containers endpoint
curl http://localhost:8000/api/v1/containers
```

### Step 2: Verify Frontend
```bash
# Check if frontend is serving
curl http://localhost:3000

# Check browser console (F12)
# Look for WebSocket connections in Network tab
```

### Step 3: Check WebSocket
```bash
# Test WebSocket connection (requires wscat or similar)
# Install: npm install -g wscat
wscat -c ws://localhost:8000/api/v1/ws/metrics
```

### Step 4: Check Logs
```bash
# Backend logs
tail -f backend.log

# Frontend logs  
tail -f frontend.log

# Docker logs
docker ps
docker logs <container_id>
```

## Browser Console Checks

Open browser DevTools (F12) and check:

1. **Console Tab:**
   - Look for WebSocket connection messages
   - Check for CORS errors
   - Verify no JavaScript errors

2. **Network Tab:**
   - Filter by "WS" (WebSocket)
   - Check if connections show "101 Switching Protocols"
   - Verify messages are being received

3. **Application Tab:**
   - Check if cookies/localStorage are blocking requests
   - Verify no service worker issues

## Quick Start (If Everything Fails)

1. **Stop everything:**
   ```bash
   pkill -f uvicorn
   pkill -f vite
   ```

2. **Start fresh:**
   ```bash
   cd container-monitoring
   ./start_dashboard.sh
   ```

3. **Or manually:**
   ```bash
   # Terminal 1
   cd backend
   source venv/bin/activate
   uvicorn backend.app.main:app --reload

   # Terminal 2
   cd frontend
   npm run dev
   ```

## Still Not Working?

1. **Check system requirements:**
   - Python 3.11+
   - Node.js 20+
   - Docker installed and running

2. **Verify installation:**
   ```bash
   # Backend
   cd backend
   source venv/bin/activate
   pip list | grep fastapi

   # Frontend
   cd frontend
   npm list | grep react
   ```

3. **Reinstall dependencies:**
   ```bash
   # Backend
   cd backend
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

   # Frontend
   cd frontend
   rm -rf node_modules
   npm install
   ```

4. **Check firewall:**
   - Ensure ports 3000, 3001, 8000 are not blocked
   - Check if antivirus is blocking connections

## Getting Help

If issues persist:
1. Run `./check_setup.sh` and share output
2. Check browser console errors (F12)
3. Check backend logs
4. Verify Docker is running: `docker ps`
