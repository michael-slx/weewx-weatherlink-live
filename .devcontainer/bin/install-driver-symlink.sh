#!/usr/bin/env bash
set -e

STATION_DIR="$HOME/weewx-data"

if [ -s "$STATION_DIR/bin/user/weatherlink_live" ]; then
  echo "Removing old symlink"
  rm "$STATION_DIR/bin/user/weatherlink_live"
fi

ln -vs "$(pwd)/bin/user/weatherlink_live" "$STATION_DIR/bin/user/weatherlink_live"
cp -v "$(pwd)/.devcontainer/weewx.conf" "$STATION_DIR/weewx.conf"
