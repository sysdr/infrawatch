#!/bin/bash
cd "$(dirname "$0")"
export HOST=0.0.0.0
export PORT=3000
export BROWSER=none
npm start
