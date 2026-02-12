#!/bin/bash
# Fix Docker "load metadata" / credential errors on WSL (e.g. docker-credential-desktop.exe)
# Run once: ./scripts/fix-docker-credentials.sh

CONFIG="$HOME/.docker/config.json"
BACKUP="$HOME/.docker/config.json.bak"

if [ ! -f "$CONFIG" ]; then
  echo "No Docker config found at $CONFIG"
  exit 0
fi

if grep -q '"credsStore"' "$CONFIG" 2>/dev/null; then
  echo "Backing up $CONFIG to $BACKUP"
  cp "$CONFIG" "$BACKUP"
  # Remove credsStore so Docker pulls without the broken helper
  if command -v jq &>/dev/null; then
    jq 'del(.credsStore)' "$BACKUP" > "$CONFIG"
  else
    sed -i '/"credsStore"/d' "$CONFIG"
  fi
  echo "Removed credsStore from Docker config. Try: docker pull node:18-alpine"
else
  echo "Docker config has no credsStore. If pull still fails, check network or try: docker logout"
fi
