# Backend Fix - Correct Startup Instructions

## Issue Fixed

The backend was failing because it needs to be run from the **container-monitoring** directory (parent directory), not from inside the backend directory. This is required for the relative imports to work correctly.

## ✅ Correct Way to Start Backend

### Option 1: Use the Startup Script (Recommended)

```bash
cd container-monitoring
./run_backend.sh
```

### Option 2: Manual Start (From container-monitoring directory)

```bash
cd container-monitoring
source backend/venv/bin/activate
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Important:** Must run from `container-monitoring` directory, NOT from `backend` directory!

## ✅ Correct Way to Start Frontend

### Option 1: Use the Startup Script

```bash
cd container-monitoring
./run_frontend.sh
```

### Option 2: Manual Start

```bash
cd container-monitoring/frontend
npm run dev
```

## 🔗 Backend Links (When Running)

Once the backend is started, access:

- **API Base:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Interactive API:** http://localhost:8000/docs (Swagger UI)
- **Alternative Docs:** http://localhost:8000/redoc (ReDoc)

## 🔗 Dashboard Links (When Running)

Once the frontend is started, access:

- **Dashboard:** http://localhost:3000
- **Or:** http://localhost:3001 (if 3000 is in use)
- **Check terminal output** for the actual port

## Quick Start (Both Services)

**Terminal 1 - Backend:**
```bash
cd container-monitoring
./run_backend.sh
```

**Terminal 2 - Frontend:**
```bash
cd container-monitoring
./run_frontend.sh
```

## Verify Backend is Working

1. **Check health:**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy","service":"container-monitoring"}`

2. **Open API docs:**
   Open browser to: http://localhost:8000/docs

3. **Test WebSocket:**
   Check browser console when dashboard loads - should see "Metrics WebSocket connected"

## Common Errors Fixed

### ❌ Wrong (from backend directory):
```bash
cd backend
uvicorn backend.app.main:app  # This fails with import errors
```

### ✅ Correct (from container-monitoring directory):
```bash
cd container-monitoring
uvicorn backend.app.main:app  # This works!
```

## Why This Matters

The backend uses relative imports like:
- `from ..api.routes import router`
- `from ..models.container import ContainerInfo`

These imports require Python to see `backend` as a package, which only works when running from the parent directory (`container-monitoring`).

## Troubleshooting

If backend still doesn't start:

1. **Check Python version:**
   ```bash
   python3 --version  # Should be 3.11+
   ```

2. **Reinstall dependencies:**
   ```bash
   cd container-monitoring/backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Check port 8000:**
   ```bash
   lsof -i :8000  # See if port is in use
   ```

4. **Check Docker:**
   ```bash
   docker info  # Backend needs Docker access
   ```

## Expected Output

When backend starts correctly, you should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Container Monitoring API started
INFO:     Application startup complete.
```

Then the dashboard at http://localhost:3000 should show "Connected" status!
