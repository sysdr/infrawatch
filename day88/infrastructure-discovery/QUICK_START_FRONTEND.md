# Quick Start Guide

## To Start the Frontend (Once Dependencies Are Installed)

### Option 1: Use the Simple Starter Script
```bash
cd infrastructure-discovery
./start-frontend.sh
```

### Option 2: Manual Start
```bash
cd infrastructure-discovery/frontend
PORT=3001 BROWSER=none node node_modules/react-scripts/scripts/start.js
```

### Option 3: Using the Dev Script
```bash
cd infrastructure-discovery/frontend
PORT=3001 ./start-dev.sh
```

## Current Status

✅ **Dependencies are installing** (npm install is running)
⏳ **Wait 2-5 minutes** for installation to complete
✅ **Then run** `./start-frontend.sh` to start the frontend

## Once Started

1. Wait 30-60 seconds for compilation
2. Look for "Compiled successfully!" message
3. Open **http://localhost:3001** in your browser

## Files Created

- `start-frontend.sh` - Main starter script (waits for dependencies)
- `frontend/start-dev.sh` - Frontend-specific starter
- `FRONTEND_FIX.md` - Detailed troubleshooting guide
