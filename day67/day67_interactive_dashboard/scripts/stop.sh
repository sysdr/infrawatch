#!/bin/bash

echo "Stopping Interactive Dashboard System..."

if [ -f /tmp/dashboard_backend.pid ]; then
    kill $(cat /tmp/dashboard_backend.pid) 2>/dev/null || true
    rm /tmp/dashboard_backend.pid
fi

if [ -f /tmp/dashboard_frontend.pid ]; then
    kill $(cat /tmp/dashboard_frontend.pid) 2>/dev/null || true
    rm /tmp/dashboard_frontend.pid
fi

echo "✅ Stopped"
