# Solution for ERR_CONNECTION_REFUSED

## Problem
The frontend is not accessible because:
1. The frontend server is not running, OR
2. The frontend is still compiling (takes 30-60 seconds), OR  
3. Dependencies are incomplete/corrupted

## Complete Solution

### Step 1: Kill any existing processes
```bash
pkill -f "react-scripts"
pkill -f "npm start"
```

### Step 2: Ensure dependencies are installed
```bash
cd infrastructure-discovery/frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

### Step 3: Start the frontend
```bash
cd infrastructure-discovery/frontend
PORT=3001 BROWSER=none npm start
```

**OR use the background script:**
```bash
cd infrastructure-discovery
./scripts/start-frontend.sh
```

### Step 4: Wait for compilation
- First compilation: 30-60 seconds
- Look for: "Compiled successfully!" message
- The server will be available at http://localhost:3001

### Step 5: Verify it's working
```bash
curl http://localhost:3001
# Should return HTML content
```

## Alternative: Use Docker
If npm issues persist, use Docker:

```bash
cd infrastructure-discovery/docker
docker-compose up frontend
```

## Current Status
- Frontend process is running (check with: `ps aux | grep react-scripts`)
- May still be compiling (wait 30-60 seconds)
- Will be available at http://localhost:3001 when ready

## Troubleshooting

**If port 3001 is in use:**
```bash
ss -tlnp | grep 3001  # Check what's using it
PORT=3002 npm start    # Use different port
```

**If you see permission errors:**
```bash
chmod -R u+w node_modules/.bin
```

**If compilation fails:**
- Check for syntax errors in src/ files
- Check browser console for errors
- Review /tmp/frontend*.log files

## Quick Test
```bash
# Check if process is running
ps aux | grep react-scripts

# Check if port is listening
ss -tlnp | grep 3001

# Test connection
curl http://localhost:3001
```
