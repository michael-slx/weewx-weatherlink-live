#!/usr/bin/env bash
set -e

SOURCE_DIR="/vagrant/bin/user/weatherlink_live"
TARGET_DIR="/usr/lib/weewx/user/weatherlink_live"

[[ -d "$(dirname "$TARGET_DIR")" ]] || (echo "Creating $(dirname "$TARGET_DIR")" && mkdir -p "$(dirname "$TARGET_DIR")")
[[ -d "$TARGET_DIR" ]] && (echo "Removing $TARGET_DIR" && rm -fR "$TARGET_DIR")

cp -R "$SOURCE_DIR" "$TARGET_DIR"