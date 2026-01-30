#!/bin/bash
# Start backend and frontend. Use full path so this works from any cwd.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$SCRIPT_DIR/scripts/start.sh" "$@"
