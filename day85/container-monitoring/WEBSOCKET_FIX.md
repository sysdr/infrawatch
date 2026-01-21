# WebSocket Connection Fix

## Issues Fixed

### 1. CORS Configuration
- **Problem:** Backend only allowed connections from ports 3000 and 5173
- **Fix:** Added support for all common localhost ports (3000, 3001, 3002, 5173)
- **File:** `backend/app/main.py`

### 2. WebSocket URL Generation
- **Problem:** URL might not include correct port
- **Fix:** Improved URL generation to properly handle window.location.host
- **File:** `frontend/src/hooks/useWebSocket.js`

### 3. Vite Proxy Configuration
- **Problem:** WebSocket proxy might not be working correctly
- **Fix:** Added proxy error handling and logging
- **File:** `frontend/vite.config.js`

### 4. Connection Fallback
- **Problem:** If proxy fails, connection would fail completely
- **Fix:** Added automatic fallback to direct connection (ws://localhost:8000)
- **File:** `frontend/src/hooks/useWebSocket.js`

## How It Works Now

1. **First Attempt:** Tries to connect through Vite proxy (ws://localhost:3001/api/v1/ws/metrics)
2. **If Proxy Fails:** Automatically falls back to direct connection (ws://localhost:8000/api/v1/ws/metrics)
3. **Retry Logic:** Exponential backoff with up to 5 retries
4. **Connection Status:** Shows "Connected" when WebSocket is established

## Testing the Fix

1. **Start Backend:**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Check Browser Console:**
   - Open DevTools (F12)
   - Look for: "Attempting to connect via proxy: ws://localhost:3001/api/v1/ws/metrics"
   - Or: "Using direct connection to: ws://localhost:8000/api/v1/ws/metrics"
   - Should see: "Metrics WebSocket connected"

4. **Verify Connection:**
   - Dashboard should show green "Connected" badge
   - No error messages
   - If containers exist, they should appear

## Troubleshooting

### Still Showing "Disconnected"?

1. **Check Backend:**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy","service":"container-monitoring"}`

2. **Check Browser Console:**
   - Look for WebSocket connection errors
   - Check Network tab → WS filter
   - Verify connection shows "101 Switching Protocols"

3. **Try Direct Connection:**
   - Open browser console
   - Run: `new WebSocket('ws://localhost:8000/api/v1/ws/metrics')`
   - Check if it connects

4. **Check Firewall:**
   - Ensure ports 3000-3002 and 8000 are not blocked
   - Check if antivirus is blocking WebSocket connections

### Connection Drops Frequently?

1. **Check Backend Logs:**
   ```bash
   tail -f backend.log
   ```
   Look for WebSocket errors

2. **Check Network:**
   - Ensure stable network connection
   - Check for proxy/VPN interference

3. **Increase Timeout:**
   - Backend sends ping every 30 seconds
   - Frontend retries with exponential backoff

## Expected Behavior

✅ **Connected State:**
- Green "Connected" badge
- Console shows "Metrics WebSocket connected"
- Receives data every second (if containers exist)
- No error messages

❌ **Disconnected State:**
- Red "Disconnected" badge
- Error message in alert
- Console shows connection errors
- Automatic retry attempts

## Manual Connection Test

Test WebSocket connection directly:

```javascript
// In browser console
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/metrics');
ws.onopen = () => console.log('Connected!');
ws.onmessage = (e) => console.log('Message:', e.data);
ws.onerror = (e) => console.error('Error:', e);
ws.onclose = (e) => console.log('Closed:', e.code, e.reason);
```

If this works, the issue is with the frontend code. If it doesn't, the issue is with the backend.
