# Frontend install (WSL + Windows filesystem)

If you see **Module not found** (antd, axios, recharts, etc.) or **EACCES/permission denied** when running `npm install`, the project is likely on the Windows filesystem (`/mnt/c/...`), which breaks npm in WSL.

## Fix: use a WSL-native path

1. **Clone or copy the project into a WSL directory** (not under `/mnt/c/`):
   ```bash
   cp -r /mnt/c/Users/systemdr2/wsl-shared/infrawatch/day92 /home/sdr/day92-frontend-run
   cd /home/sdr/day92-frontend-run/log-aggregation/frontend
   ```

2. **Clean install**:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Start the frontend**:
   ```bash
   npm start
   ```
   Or from the project root: `./start.sh`

## If you must keep the project on C:\

- Run the **frontend** from Windows: open the folder in VS Code/Cursor on Windows, open a terminal there, and run `npm install` and `npm start` from that Windows terminal (use Node from Windows, not WSL).
- Keep using WSL only for backend/Postgres/Redis if you prefer.

## Already set in this project

- `DISABLE_ESLINT_PLUGIN=true` in `.env` to avoid ESLint config errors.
- `HOST=0.0.0.0` and `PORT=3000` in `.env` for access from the browser.
