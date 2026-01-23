# Quick Start Guide - Fixing Connection Refused Error

## Problem
Getting `ERR_CONNECTION_REFUSED` when trying to access localhost.

## Solution

### Step 1: Start the Frontend
The frontend needs to be running. Use one of these methods:

**Method A - Using the startup script:**
```bash
cd infrastructure-discovery
./scripts/start-frontend.sh
```

**Method B - Manual start:**
```bash
cd infrastructure-discovery/frontend
PORT=3001 BROWSER=none node node_modules/react-scripts/bin/react-scripts.js start
```

**Method C - Using npm (if permissions are fixed):**
```bash
cd infrastructure-discovery/frontend
PORT=3001 BROWSER=none npm start
```

### Step 2: Wait for Compilation
React apps take 30-60 seconds to compile the first time. Wait until you see:
```
Compiled successfully!
```

### Step 3: Access the Frontend
Once compiled, access at:
- **http://localhost:3001** (or 3000 if available)

### Step 4: Start Backend (if needed)
```bash
cd infrastructure-discovery/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Troubleshooting

**If port is in use:**
- Check: `ss -tlnp | grep 3001`
- Kill existing: `pkill -f "react-scripts"`
- Use different port: `PORT=3002 npm start`

**If dependencies are missing:**
```bash
cd infrastructure-discovery/frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

**If permissions denied:**
```bash
cd infrastructure-discovery/frontend
chmod -R u+w node_modules/.bin
```

## Current Status
- Frontend process is running (PID 89808)
- Compiling... (wait 30-60 seconds)
- Will be available at http://localhost:3001 when ready
