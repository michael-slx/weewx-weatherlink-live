#!/usr/bin/env bash

STATION_DIR="$HOME/weewx-data"

if [ -d "$STATION_DIR" ]; then
  echo "Removing existing station directory: $STATION_DIR"
  rm -R "$STATION_DIR"
fi

echo "Creating station directory: $STATION_DIR"
.venv/bin/weectl station create "$STATION_DIR" --no-prompt >/dev/null
