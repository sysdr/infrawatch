#!/bin/bash
set -e
echo "Day 92: Log Aggregation System Setup"
mkdir -p log-aggregation/{backend,frontend,shipper,data/{logs,parsed,archived},tests,docker}
cd log-aggregation
