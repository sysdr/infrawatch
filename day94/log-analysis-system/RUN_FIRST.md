# Fix "localhost refused to connect" (ERR_CONNECTION_REFUSED)

This means **nothing is listening** on the port. Start the servers first.

## Option A – Background (you can close the terminal)

```bash
cd /home/sdr/git/infrawatch/day94/log-analysis-system
./start-in-background.sh
```

Wait 1–2 minutes, then open **http://localhost:3001** in your browser. To stop later: `./stop.sh`

## Option B – Foreground (keep terminal open)

1. Open a **terminal**.
2. Run:
   ```bash
   cd /home/sdr/git/infrawatch/day94/log-analysis-system
   ./start.sh
   ```
3. **Leave the terminal open.** Wait 1–2 minutes until you see "webpack compiled".
4. Open in your browser: **http://localhost:3001**

---

## If you still get "refused to connect"

1. Stop everything and free ports:
   ```bash
   cd /home/sdr/git/infrawatch/day94/log-analysis-system
   ./stop.sh
   ```
2. Wait a few seconds, then start again:
   ```bash
   ./start.sh
   ```
3. Keep the terminal open and wait for the frontend to finish compiling before opening http://localhost:3001

---

## Two terminals (alternative)

- **Terminal 1:** `./start_backend.sh` (leave running)
- **Terminal 2:** `./start_frontend.sh` (leave running)
- Then open **http://localhost:3001**
