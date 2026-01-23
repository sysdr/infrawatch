# Complete Solution: Fix ERR_CONNECTION_REFUSED

## Current Status
- Dependencies are installing (this takes 2-5 minutes)
- Once complete, the frontend can be started

## Step-by-Step Solution

### Step 1: Wait for Dependencies to Install
Check if installation is complete:
```bash
cd infrastructure-discovery/frontend
test -d node_modules/webpack && echo "✅ Ready" || echo "⏳ Still installing..."
```

### Step 2: Start the Frontend
Once dependencies are installed, run:

```bash
cd infrastructure-discovery/frontend
PORT=3001 BROWSER=none ./start-dev.sh
```

**OR manually:**
```bash
cd infrastructure-discovery/frontend
PORT=3001 BROWSER=none node node_modules/react-scripts/scripts/start.js
```

**OR use npm (if permissions are fixed):**
```bash
cd infrastructure-discovery/frontend
PORT=3001 BROWSER=none npm start
```

### Step 3: Wait for Compilation
- First compilation: 30-60 seconds
- Look for: "Compiled successfully!" or "You can now view..."
- Server will be available at **http://localhost:3001**

### Step 4: Access the Frontend
Open in browser: **http://localhost:3001**

## Quick Start Script

I've created `start-dev.sh` in the frontend directory. Use it like this:

```bash
cd infrastructure-discovery/frontend
PORT=3001 ./start-dev.sh
```

This script will:
1. Check if dependencies are installed
2. Install missing dependencies if needed
3. Start the frontend server

## Troubleshooting

**If you see "Permission denied":**
```bash
cd infrastructure-discovery/frontend
chmod +x start-dev.sh
chmod -R u+w node_modules/.bin 2>/dev/null
```

**If dependencies are corrupted:**
```bash
cd infrastructure-discovery/frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

**If port 3001 is in use:**
```bash
ss -tlnp | grep 3001  # Check what's using it
PORT=3002 ./start-dev.sh  # Use different port
```

**To run in background:**
```bash
cd infrastructure-discovery/frontend
PORT=3001 nohup ./start-dev.sh > frontend.log 2>&1 &
```

## Verify It's Working

```bash
# Check if port is listening
ss -tlnp | grep 3001

# Test connection
curl http://localhost:3001

# Check process
ps aux | grep react-scripts
```

## Expected Output

When the frontend starts successfully, you should see:
```
Compiled successfully!

You can now view infrastructure-discovery-ui in the browser.

  Local:            http://localhost:3001
  On Your Network:  http://192.168.x.x:3001
```

Then open **http://localhost:3001** in your browser!
