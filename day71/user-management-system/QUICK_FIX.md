# Quick Fix for Registration Issue

## Problem
Registration is failing with 400 Bad Request because PostgreSQL is not running.

## Solution

### Option 1: Start PostgreSQL (Recommended)
```bash
# Start PostgreSQL service
sudo systemctl start postgresql

# Or if using service command
sudo service postgresql start

# Verify it's running
pg_isready -h localhost -p 5432

# Create database if it doesn't exist
sudo -u postgres createdb user_management
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
```

### Option 2: Use Docker (Easiest)
```bash
./build.sh docker
```

This will start PostgreSQL, Redis, backend, and frontend automatically.

### Option 3: Check PostgreSQL Configuration
If PostgreSQL is installed but not accepting connections:

```bash
# Check if PostgreSQL is listening
sudo netstat -tlnp | grep 5432

# Check PostgreSQL status
sudo systemctl status postgresql

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

## After Starting PostgreSQL

1. **Restart the backend server** (if it's running):
   - The backend should auto-reload, but if errors persist, restart it
   
2. **Try registering again** - you should now see:
   - Clear error messages if something else is wrong
   - Successful registration if everything is working

## React Router Warnings

The React Router warnings should disappear after:
1. The frontend reloads (it should auto-reload with Vite)
2. Or do a hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

The future flags are already configured in `frontend/src/App.jsx`.


