#!/usr/bin/env bash
set -e

SRC_DIR="/vagrant"

declare sudo_cmd
if [[ -d "/usr/lib/weewx/bin/user" ]]; then
    sudo_cmd="sudo"
elif [[ -d "$HOME/weewx-data/bin/user" ]]; then
    sudo_cmd=""
else
    echo "Could not determine target directory"
    echo "Have you installed WeeWX?"
    exit 2
fi

$sudo_cmd weectl extension install "$SRC_DIR" --yes
