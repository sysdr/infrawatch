#!/usr/bin/env bash
# Wrapper so ./build.sh runs the same as ./setup.sh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$SCRIPT_DIR/setup.sh" "$@"
