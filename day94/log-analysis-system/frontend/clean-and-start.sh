#!/bin/bash
# Force clean build so dashboard shows current code (no Backend URL / unreachable banner).
set -e
cd "$(dirname "$0")"
echo "Clearing cache..."
rm -rf node_modules/.cache .eslintcache 2>/dev/null || true
echo "Cache cleared. Start the dev server with: npm start"
echo "Then in the browser: hard refresh (Ctrl+Shift+R) or open in incognito."
