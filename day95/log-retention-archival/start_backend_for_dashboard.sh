#!/bin/bash
# Start backend so the dashboard can reach it. Waits until http://localhost:8000 responds.
cd "$(dirname "$0")"
echo "Starting backend..."
docker compose up -d backend
echo "Waiting for backend at http://localhost:8000 ..."
for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ 2>/dev/null | grep -q 200; then
    echo "Backend is ready. Dashboard can now reach http://localhost:8000"
    exit 0
  fi
  sleep 1
done
echo "Backend may still be starting. Try refreshing the dashboard in a few seconds."
