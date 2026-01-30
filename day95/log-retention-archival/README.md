# Log Retention & Archival System

**Dashboard:** http://localhost:3000  
*(Use exactly that URL — not www.localhost.com. No "www", no ".com".)*

**Simplest way (no npm, no Docker for frontend):**  
Run `./serve_dashboard.sh` then open **http://localhost:3000** — uses Python's built-in server and a single HTML file.

### If you see "react-scripts: Permission denied" or "ERR_CONNECTION_REFUSED"
- **Recommended (Docker):** Run `./scripts/start_dashboard_docker.sh` — wait ~1–2 min, then open **http://localhost:3000**
- **Option A (Docker):** Or start the frontend in Docker manually so it listens on 0.0.0.0:  
  `docker compose up -d frontend`  
  Wait ~1 minute for the dev server to compile, then open http://localhost:3000
- **Option B (local):** Run the frontend with `HOST=0.0.0.0` so it’s reachable:  
  `./scripts/start_frontend.sh` or `cd frontend && HOST=0.0.0.0 npm start`  
  (On WSL, if `npm install` fails with EACCES, use Option A or run the project from a Linux path, e.g. under `/home`.)

## Quick Start

### With Docker (recommended)
```bash
# From project root (log-retention-archival)
docker compose up -d --build
# Wait ~30s for backend to be ready, then:
./scripts/run_demo.sh    # Populate dashboard with sample data
# Open http://localhost:3000 - metrics will be non-zero
```

### Without Docker (requires PostgreSQL, Redis, MinIO)
```bash
# Start backend (from project root)
./scripts/start_backend.sh   # or: cd backend && source venv/bin/activate && PYTHONPATH=. python api/main.py

# In another terminal, start frontend
./scripts/start_frontend.sh  # or: cd frontend && npm start

# Populate dashboard
./scripts/run_demo.sh
# Open http://localhost:3000
```

### Duplicate services
If ports 8000 or 3000 are already in use:
- `KILL_DUPLICATES=1 ./scripts/start.sh` to auto-kill existing processes, or
- Stop manually: `pkill -f "api/main.py"` and/or `pkill -f "react-scripts"`

## Dashboard validation
1. Open http://localhost:3000 (Overview).
2. If all metrics are 0, click **Generate Sample Logs** (Quick Actions).
3. Stats (Hot/Warm/Cold logs, Total Cost) and charts update automatically.
4. Optionally click **Evaluate Retention** to create archival jobs.

## Run tests
```bash
cd backend && PYTHONPATH=. pytest ../tests/test_retention.py -v
```

## Scripts (use full path)
- `./scripts/start.sh` – start backend + frontend (checks for duplicate ports).
- `./scripts/start_backend.sh` – backend only.
- `./scripts/start_frontend.sh` – frontend only.
- `./scripts/run_demo.sh` – generate sample logs so dashboard shows non-zero values.
