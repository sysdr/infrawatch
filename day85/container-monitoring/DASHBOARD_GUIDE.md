# Container Monitoring Dashboard - User Guide

## Quick Start

### 1. Start the Dashboard

```bash
cd container-monitoring
./start_dashboard.sh
```

Or manually:

**Terminal 1 - Backend:**
```bash
cd container-monitoring/backend
source venv/bin/activate
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd container-monitoring/frontend
npm run dev
```

### 2. Access the Dashboard

Open your browser and navigate to:
- **Dashboard:** http://localhost:3000 (or the port shown in terminal)
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## Dashboard Features

### Connection Status

The top-right corner shows the connection status:
- 🟢 **Connected** - WebSocket is connected and receiving data
- 🔴 **Disconnected** - WebSocket connection failed (check backend)

### Container List (Left Panel)

- Shows all running Docker containers
- Displays container name, image, and status
- Shows real-time CPU and Memory usage as chips
- Click a container to view detailed metrics

**Status Colors:**
- 🟢 Green - Running
- 🔴 Red - Exited/Stopped
- 🟡 Yellow - Paused

### Metrics Charts (Center Panel)

When a container is selected, you'll see:

1. **Health Status**
   - Current health check status
   - Failing streak count
   - Health check logs

2. **CPU Usage Chart**
   - Real-time CPU percentage
   - Baseline reference line
   - 60-second rolling window

3. **Memory Usage Chart**
   - Real-time memory percentage
   - Baseline reference line
   - 60-second rolling window

### Alerts Panel (Bottom Left)

- Shows active alerts for all containers
- Color-coded by severity:
  - 🔴 **Critical** - Immediate attention required
  - 🟡 **Warning** - Monitor closely
- Alerts include:
  - CPU usage thresholds
  - Memory usage thresholds
  - Health check failures
  - Frequent restarts

### Event Stream (Bottom Right)

- Real-time Docker events
- Container lifecycle events:
  - Start, Stop, Restart
  - Pause, Unpause
  - Die, Kill, Remove
- Timestamped events
- Exit codes for stopped containers

## Testing the Dashboard

### Test 1: Empty State

1. Stop all containers: `docker stop $(docker ps -q)`
2. Refresh dashboard
3. Should show "No containers running"
4. Connection status should be "Connected"

### Test 2: Single Container

1. Start a test container:
   ```bash
   docker run -d --name test-nginx nginx
   ```
2. Dashboard should show the container
3. Click on it to see metrics
4. CPU and Memory charts should update every second

### Test 3: Multiple Containers

1. Start multiple containers:
   ```bash
   docker run -d --name web1 nginx
   docker run -d --name web2 nginx
   docker run -d --name redis redis:alpine
   ```
2. All containers should appear in the list
3. Switch between them to see different metrics

### Test 4: Alerts

1. Create a container with resource limits:
   ```bash
   docker run -d --name stress-test --memory="100m" --cpus="0.5" \
     progrium/stress --cpu 1 --timeout 60s
   ```
2. Watch for CPU/Memory alerts in the Alerts panel
3. Alerts should appear when thresholds are exceeded

### Test 5: Events

1. Start a container: `docker start test-nginx`
2. Check Event Stream for "start" event
3. Stop it: `docker stop test-nginx`
4. Check Event Stream for "stop" event

## Troubleshooting

### Dashboard Shows "Disconnected"

1. **Check Backend:**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy","service":"container-monitoring"}`

2. **Check WebSocket:**
   - Open browser DevTools (F12)
   - Go to Network tab → WS (WebSocket)
   - Should see connections to `/api/v1/ws/metrics` and `/api/v1/ws/events`
   - Status should be "101 Switching Protocols"

3. **Check Backend Logs:**
   ```bash
   tail -f backend.log
   ```

### No Containers Showing

1. **Check Docker:**
   ```bash
   docker ps
   ```
   Should show running containers

2. **Check Docker Socket:**
   ```bash
   ls -l /var/run/docker.sock
   ```
   Backend needs access to Docker socket

3. **Check Backend Logs:**
   Look for Docker connection errors

### Metrics Not Updating

1. **Verify WebSocket Connection:**
   - Check browser console for errors
   - Verify WebSocket messages are being received

2. **Check Container Status:**
   - Container must be running (not paused/stopped)
   - Some containers may not report stats

3. **Refresh Dashboard:**
   - Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

## API Endpoints

### REST API

- `GET /api/v1/containers` - List all containers
- `GET /api/v1/containers/{id}/metrics` - Get container metrics
- `GET /api/v1/containers/{id}/health` - Get container health
- `GET /api/v1/containers/{id}/history` - Get metrics history
- `GET /api/v1/alerts` - Get active alerts

### WebSocket

- `WS /api/v1/ws/metrics` - Real-time metrics stream
- `WS /api/v1/ws/events` - Docker events stream

## Performance Tips

1. **Limit Container Count:**
   - Dashboard works best with < 50 containers
   - Large numbers may slow down updates

2. **Browser Performance:**
   - Close other tabs to free memory
   - Use Chrome/Edge for best performance

3. **Network:**
   - WebSocket updates every 1 second
   - Ensure stable network connection

## Keyboard Shortcuts

- **F5** - Refresh page
- **Ctrl+R / Cmd+R** - Refresh
- **Ctrl+Shift+R / Cmd+Shift+R** - Hard refresh (clear cache)
- **F12** - Open DevTools

## Screenshots

The dashboard includes:
- Real-time metrics visualization
- Color-coded status indicators
- Responsive Material-UI design
- Professional monitoring interface

## Support

For issues or questions:
1. Check backend logs: `tail -f backend.log`
2. Check frontend logs: `tail -f frontend.log`
3. Review browser console (F12)
4. Check API docs: http://localhost:8000/docs
