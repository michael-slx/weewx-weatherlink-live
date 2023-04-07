#!/usr/bin/env bash
set -e

SOURCE_FILES=(
    "weatherlink_live_driver.py"
    "weatherlink_live"
)

SOURCE_DIR="/vagrant/bin/user"

declare use_sudo=0
declare target_dir

if [[ -d "/usr/lib/weewx/user" ]]; then
    use_sudo=1
    target_dir="/usr/lib/weewx/user"
elif [[ -d "$HOME/weewx-data/bin/user" ]]; then
    use_sudo=0
    target_dir="$HOME/weewx-data/bin/user"
else
    echo "Could not determine target directory"
    echo "Have you installed WeeWX?"
    exit 2
fi

echo "Target directory: $target_dir"

for file in "${SOURCE_FILES[@]}"; do
    source_path="${SOURCE_DIR}/${file}"
    target_path="${TARGET_DIR}/${file}"

    if [[ -e "$target_path" ]]; then
        rm -fR "$target_path"
    fi

    if [[ $use_sudo -eq 1 ]]; then
        sudo cp -R "$source_path" "$target_dir"
    else
        cp -R "$source_path" "$target_dir"
    fi
done
