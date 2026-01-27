# Connection Refused Fix

## Issue Summary
You were getting "ERR_CONNECTION_REFUSED" because:
- ✅ **Backend** is running correctly on port 8000
- ❌ **Frontend** was not running on port 3000

## Root Cause
1. Frontend dependencies (npm install) were still installing
2. Previous frontend startup failed due to permission issues with react-scripts

## Current Status
- Backend: ✅ Running at http://localhost:8000
- Frontend: ⏳ Waiting for npm install to complete, then will auto-start

## Solutions

### Option 1: Wait for Auto-Start (Recommended)
An auto-start script is running in the background. Once npm install completes, the frontend will automatically start.

Check status:
```bash
# Check if frontend is running
curl http://localhost:3000

# Check frontend logs
tail -f frontend.log

# Check if npm install is done
pgrep -f "npm install" || echo "npm install completed"
```

### Option 2: Manual Start
Once npm install completes, run:
```bash
cd infrastructure-integration-testing
./fix-and-start.sh
```

### Option 3: Quick Manual Start
```bash
cd infrastructure-integration-testing/frontend

# Wait for npm install (if still running)
while pgrep -f "npm install" > /dev/null; do sleep 5; done

# Fix permissions and start
chmod +x node_modules/.bin/* 2>/dev/null
BROWSER=none npx react-scripts start
```

## Verify Services

```bash
# Check backend
curl http://localhost:8000/health

# Check frontend (once started)
curl http://localhost:3000

# Check what's listening on ports
netstat -tuln | grep -E ":(3000|8000)"
# or
ss -tuln | grep -E ":(3000|8000)"
```

## Access URLs
- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:3000 (once started)
- **API Documentation**: http://localhost:8000/docs

## Troubleshooting

If frontend still doesn't start:
1. Check logs: `tail -f frontend.log`
2. Verify dependencies: `ls -la frontend/node_modules/.bin/react-scripts`
3. Reinstall if needed: `cd frontend && rm -rf node_modules && npm install`
4. Start manually: `cd frontend && BROWSER=none npx react-scripts start`
