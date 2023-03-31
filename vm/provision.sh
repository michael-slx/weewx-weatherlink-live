#!/usr/bin/env bash

set -e

yay -Syyuu --noconfirm weewx python-requests

export_str="export PATH=\"\$PATH:/vagrant/vm/bin\""

if ! grep -q "$export_str" "/home/vagrant/.zshrc" >/dev/null; then
  echo "$export_str" | sudo tee -a /home/vagrant/.zshrc
fi
