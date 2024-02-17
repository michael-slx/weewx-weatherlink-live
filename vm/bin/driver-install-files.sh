#!/usr/bin/env bash
set -e

SOURCE_DIR="/vagrant/bin/user"
SOURCE_FILES=("weatherlink_live" "weatherlink_live_driver.py")

declare sudo_cmd
declare target_dir
if [[ -d "/usr/lib/weewx/bin/user" ]]; then
    sudo_cmd="sudo"
    target_dir="/usr/lib/weewx/bin/user"
elif [[ -d "$HOME/weewx-data/bin/user" ]]; then
    sudo_cmd=""
    target_dir="$HOME/weewx-data/bin/user"
else
    echo "Could not determine target directory"
    echo "Have you installed WeeWX?"
    exit 2
fi

for file in "${SOURCE_FILES[@]}"; do
    source_path="${SOURCE_DIR}/${file}"
    target_path="${target_dir}/${file}"
    echo "$source_path -> $target_path"

    if [[ -e "$target_path" ]]; then
        $sudo_cmd rm -fR "$target_path"
    fi

    if [[ -d "$source_path" ]]; then
        $sudo_cmd mkdir -p "$target_path"
        $sudo_cmd cp -R "$source_path"/* "$target_path"
    else
        $sudo_cmd cp -R "$source_path" "$target_path"
    fi
done
