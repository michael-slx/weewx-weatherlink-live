#!/usr/bin/env bash

set -e

PACKAGES=(
  "python"
  "python-pip"
  "python-pipx"
)
PATH_ENTRIES=(
  "$HOME/.local/bin"
  "/vagrant/vm/bin"
)

yay -Syy --noconfirm archlinux-keyring 
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
- Use ${standout}weewx-install.sh${normal} to install the current WeeWX version
- Use ${standout}weewx-5-install.sh${normal} to install the WeeWX 5 alpha version directly
  from the repository

Then, use one of the driver scripts to install the driver:
- Use ${standout}driver-install-files.sh${normal} to install the driver by copying files
- Use ${standout}driver-install-extension.sh${normal} to install the driver using wee_extension
  or weectl

Driver install scripts automatically detect the installed WeeWX version.
${bold}For WeeWX 5, the user data area has to be created first.${normal}
END
