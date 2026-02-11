#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "Pulling latest changes..."
git pull

echo "Syncing dependencies..."
uv sync

echo "Restarting service..."
sudo systemctl restart multijournal.service

echo "Done. Status:"
sudo systemctl status multijournal.service --no-pager
