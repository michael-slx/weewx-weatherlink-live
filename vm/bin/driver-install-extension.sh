#!/usr/bin/env bash
set -e

DRV_TMP_DIR="/tmp/weewx-weatherlink-live-drv"

[[ ! -e "$DRV_TMP_DIR" ]] || sudo rm -fR "$DRV_TMP_DIR"
mkdir -p "$DRV_TMP_DIR"

cp -R /vagrant/* "$DRV_TMP_DIR"

if [[ -d "/usr/lib/weewx/user" ]]; then
    sudo wee_extension --install="$DRV_TMP_DIR"
elif [[ -d "$HOME/weewx-data/bin/user" ]]; then
    weectl extension install "$DRV_TMP_DIR"
else
    echo "Could not determine target WeeWX version"
    echo "Have you installed WeeWX?"
    exit 2
fi

[[ -e "$DRV_TMP_DIR" ]] && sudo rm -fR "$DRV_TMP_DIR"
