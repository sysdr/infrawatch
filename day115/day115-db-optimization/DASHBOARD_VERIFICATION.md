# Day 115 Dashboard – Terminal Analysis & Browser Verification

## Terminal analysis summary

### Backend (API)
- **Status:** Running
- **Process:** `uvicorn app.main:app --reload --port 8000`
- **Port:** 8000
- **Log:** `/tmp/day115-api.log`
- **Health:** API responds with **503** on `/health` because PostgreSQL is not running (connection refused on port 5432). This is expected until a DB is available.

### Frontend (React dev server)
- **Status:** Not running successfully
- **Log:** `/tmp/day115-frontend.log`

Observed errors in order:

1. **`Cannot find module 'ajv/dist/compile/codegen'`**  
   - react-scripts 5.0.1 + ajv-keywords / schema-utils version mismatch.

2. **`TypeError: Cannot read properties of undefined (reading 'date')`**  
   - In `fork-ts-checker-webpack-plugin`’s nested `ajv-keywords` (format/date).  
   - Occurs after adding `ajv@^8` and overrides; nested dependency still uses an incompatible ajv-keywords.

3. **`Cannot find module 'shebang-command'`**  
   - After switching to react-scripts 4 and reinstalling, npm hit **TAR_ENTRY_ERROR** and **ENOENT** on paths under `C:\Users\...\wsl-shared\...`.  
   - So `node_modules` is incomplete/corrupt when the project is used from the WSL-shared Windows path; `shebang-command` (dependency of `cross-spawn`) is missing.

4. **npm install (react-scripts 4)**  
   - Many `npm warn tar TAR_ENTRY_ERROR ENOENT` for files under `C:\Users\systemdr2\wsl-shared\infrawatch\day115\...`  
   - Indicates npm/node running from WSL while the project lives on a Windows-mounted path (e.g. `/mnt/c/...` or `\\wsl$\...`), leading to path/length or cross-filesystem issues and incomplete installs.

---

## Is the dashboard visible in the browser?

**No.** The dashboard is not visible because:

1. The React dev server (`npm start`) does not stay up; it crashes due to the errors above.
2. Port 3000 either has no process listening or the process exits quickly.
3. There is no successful production build to serve (e.g. `npm run build` also fails with the same `shebang-command` / broken `node_modules`).

So at **http://localhost:3000** you will see connection refused, or a brief load followed by failure, not the DB Optimization Dashboard.

---

## How to get the dashboard working and verify in the browser

### Option A: Run frontend from a native Linux path (recommended in WSL)

Avoid using the project from the Windows-mounted path so npm install is complete and stable:

```bash
# Copy or clone the project into a Linux-only path, then install and start
cp -r /mnt/c/Users/systemdr2/wsl-shared/infrawatch/day115/day115-db-optimization /home/sdr/day115-work
cd /home/sdr/day115-work/frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
# Fix ajv for react-scripts 5 (if still needed):
# npm install ajv@^8.12.0 --legacy-peer-deps
REACT_APP_API_URL=http://localhost:8000 npm start
```

Then open **http://localhost:3000** in your browser. You should see the DB Optimization Dashboard (API calls may still return 503 until PostgreSQL is running).

### Option B: Run from Windows

Open the same repo in **Windows** (e.g. in PowerShell or cmd under `C:\Users\systemdr2\wsl-shared\infrawatch\day115\day115-db-optimization\frontend`), then:

```powershell
Remove-Item -Recurse -Force node_modules; Remove-Item package-lock.json -ErrorAction SilentlyContinue
npm install --legacy-peer-deps
$env:REACT_APP_API_URL="http://localhost:8000"; npm start
```

Then open **http://localhost:3000** in your browser.

### Option C: Use Docker for frontend (and API/DB)

From the project root:

```bash
cd day115-db-optimization
docker compose up -d
```

Then open **http://localhost:3000** (and **http://localhost:8000/docs** for the API). The dashboard should be visible and the API healthy once Postgres is up.

---

## Quick verification checklist

| Check | Command / action | Expected |
|-------|-------------------|----------|
| Backend process | `pgrep -af "uvicorn app.main"` | One uvicorn process |
| Backend port | `curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health` | 503 (no DB) or 200 (with DB) |
| Frontend process | `pgrep -af "react-scripts"` | One process if dev server is running |
| Frontend port | `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/` | 200 when dashboard is serving |
| Browser | Open http://localhost:3000 | “DB Optimization” dashboard with summary cards, slow queries, index health, partitions, replication |

---

## Summary

- **Terminal:** Backend runs and logs to `/tmp/day115-api.log`; frontend fails to start due to ajv/fork-ts-checker and/or broken `node_modules` (WSL/Windows path).
- **Dashboard:** Not currently visible in the browser because the frontend dev server does not run successfully.
- **Fix:** Use a native Linux path (Option A) or Windows (Option B) for `npm install` and `npm start`, or run everything with Docker (Option C), then confirm **http://localhost:3000** in the browser.
