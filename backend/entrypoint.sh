#!/bin/bash
set -e

echo "Starting server..."
exec fastapi run index.py --host 0.0.0.0 --port 8000