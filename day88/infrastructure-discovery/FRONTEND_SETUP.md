# Frontend Setup Instructions

## Issue
The frontend is not visible because:
1. Port 3000 is already in use by another project (day87)
2. Frontend dependencies may need to be reinstalled

## Solution

### Option 1: Use Port 3001 (Recommended)
The start script has been updated to use port 3001. To start the frontend:

```bash
cd infrastructure-discovery/frontend
PORT=3001 BROWSER=none npm start
```

Then access the frontend at: **http://localhost:3001**

### Option 2: Fix Dependencies
If you encounter permission or corruption issues with node_modules:

```bash
cd infrastructure-discovery/frontend
rm -rf node_modules package-lock.json
npm install
```

### Option 3: Use the Start Script
The updated start script will automatically use port 3001:

```bash
cd infrastructure-discovery
./scripts/start.sh
```

## Backend CORS
The backend has been updated to allow requests from both ports 3000 and 3001.

## Access URLs
- Frontend: http://localhost:3001 (or 3000 if available)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
