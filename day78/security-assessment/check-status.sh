#!/bin/bash
echo "=== Service Status Check ==="
echo ""
echo "Backend (Port 8000):"
if lsof -i :8000 >/dev/null 2>&1; then
    echo "  ✅ Running - http://localhost:8000"
    curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "  ⚠️  Running but not responding"
else
    echo "  ❌ Not running"
fi

echo ""
echo "Frontend (Port 3000):"
if lsof -i :3000 >/dev/null 2>&1; then
    echo "  ✅ Running - http://localhost:3000"
    WSL_IP=$(hostname -I | awk '{print $1}')
    echo "  Also try: http://$WSL_IP:3000"
else
    echo "  ⏳ Still compiling..."
    if ps aux | grep -q "[r]eact-scripts start"; then
        echo "  (Compilation in progress, this can take 1-2 minutes)"
        echo "  Check progress: tail -f /tmp/frontend.log"
    else
        echo "  ❌ Not running"
    fi
fi

echo ""
echo "Dashboard Metrics:"
curl -s http://localhost:8000/api/security/dashboard/metrics 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(f\"  Vulnerabilities: {d['vulnerabilities']['total']}\")
    print(f\"  Compliance Checks: {d['compliance']['total_checks']}\")
    print(f\"  Threats: {d['threats']['total']}\")
    print(f\"  Recent Scans: {d['activity']['recent_scans']}\")
except:
    print('  (Backend not accessible)')
" 2>/dev/null || echo "  (Unable to fetch metrics)"
