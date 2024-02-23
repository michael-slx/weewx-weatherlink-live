#!/usr/bin/env bash

set -e

PACKAGES=(
  "mkdocs"
  "mkdocs-material"
  "mkdocs-material-extensions"
  "poetry"
  "python"
  "python-cheetah3"
  "python-configobj"
  "python-pip"
  "python-pipx"
  "python-pyephem"
  "python-pymysql"
  "python-pyserial"
  "python-pyusb"
  "python-requests"
)
PATH_ENTRIES=(
  "$HOME/.local/bin"
  "/vagrant/vm/bin"
)

yay -Syy --noconfirm pacman-mirrorlist archlinux-keyring
yay -Syyuu --noconfirm "${PACKAGES[@]}" 

for path_entry in "${PATH_ENTRIES[@]}"; do
  export_str="export PATH=\"${path_entry}:\${PATH}\""
  if ! grep -q "$export_str" "/home/vagrant/.zshrc" >/dev/null; then
    echo "Adding \"$path_entry\" to \$PATH"
    echo "$export_str" >> /home/vagrant/.zshrc
  fi
done

bold="$(tput bold)"
standout="$(tput smso)"
normal="$(tput sgr0)"

cat <<END



Firstly, use the weewx scripts to install WeeWX:
- Use ${standout}weewx-install-aur.sh${normal} to install the current WeeWX version from the AUR
- Use ${standout}weewx-install-github.sh${normal} to install the current WeeWX version directly
  from the repository

Then, use one of the driver scripts to install the driver:
- Use ${standout}driver-install-files.sh${normal} to install the driver by copying files
- Use ${standout}driver-install-extension.sh${normal} to install the driver using weectl
END
