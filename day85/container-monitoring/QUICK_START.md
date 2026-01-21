# Quick Start Guide - Container Monitoring Dashboard

## 🚀 Fastest Way to Start

### Single Command (Both Services)

```bash
cd container-monitoring
./start_dashboard.sh
```

This starts both backend and frontend automatically.

## 📋 Step-by-Step Start

### Terminal 1 - Backend

```bash
cd container-monitoring
./run_backend.sh
```

**OR manually:**
```bash
cd container-monitoring
source backend/venv/bin/activate
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 - Frontend

```bash
cd container-monitoring
./run_frontend.sh
```

**OR manually:**
```bash
cd container-monitoring/frontend
npm run dev
```

## 🔗 Working Links

### Backend Links (Port 8000)

- **API Base:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs ⭐ **Interactive Swagger UI**
- **Health Check:** http://localhost:8000/health
- **ReDoc:** http://localhost:8000/redoc

### Frontend Links (Port 3000 or 3001)

- **Dashboard:** http://localhost:3000
- **Or:** http://localhost:3001 (if 3000 is in use)
- **Check terminal output** for the actual port

## ✅ Verify Everything is Working

1. **Check Backend:**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy","service":"container-monitoring"}`

2. **Open API Docs:**
   - Browser: http://localhost:8000/docs
   - Should show interactive API documentation

3. **Open Dashboard:**
   - Browser: http://localhost:3000 (or port shown in terminal)
   - Should show green "Connected" badge
   - If containers exist, they should appear

## 🐳 Test with Docker Container

To see data in the dashboard:

```bash
docker run -d --name test-nginx nginx
```

The dashboard should immediately show the container and its metrics!

## 🛑 Stop Services

**If using start_dashboard.sh:**
- Press `Ctrl+C` in the terminal

**If running separately:**
- Press `Ctrl+C` in each terminal
- Or: `pkill -f uvicorn` and `pkill -f vite`

## ❌ Troubleshooting

### Backend Won't Start

**Error:** `ImportError: attempted relative import beyond top-level package`

**Solution:** Make sure you're running from `container-monitoring` directory, NOT from `backend` directory!

```bash
# ❌ WRONG
cd backend
uvicorn backend.app.main:app

# ✅ CORRECT
cd container-monitoring
uvicorn backend.app.main:app
```

### Frontend Shows "Disconnected"

1. **Check backend is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check browser console (F12):**
   - Look for WebSocket connection errors
   - Check Network tab → WS filter

3. **Restart backend:**
   ```bash
   ./run_backend.sh
   ```

### Port Already in Use

**Backend (8000):**
```bash
lsof -i :8000
kill -9 <PID>
```

**Frontend (3000):**
- Vite will automatically use next available port (3001, 3002, etc.)
- Check terminal output for actual port

## 📊 Expected Dashboard View

When everything works:
- ✅ Green "Connected" badge (top-right)
- ✅ Container list (left panel)
- ✅ Real-time metrics charts (center)
- ✅ Alerts panel (bottom-left)
- ✅ Event stream (bottom-right)

## 🎯 Quick Test Checklist

- [ ] Backend starts without errors
- [ ] http://localhost:8000/health returns OK
- [ ] http://localhost:8000/docs opens
- [ ] Frontend starts without errors
- [ ] Dashboard shows "Connected"
- [ ] No errors in browser console
- [ ] WebSocket connections established (check DevTools → Network → WS)

## 📝 Notes

- Backend **must** run from `container-monitoring` directory
- Frontend can run from `frontend` directory
- Both services need to be running for dashboard to work
- Docker must be running for container monitoring features

---

**Dashboard Link:** http://localhost:3000 (or check terminal for actual port)
**API Docs Link:** http://localhost:8000/docs
