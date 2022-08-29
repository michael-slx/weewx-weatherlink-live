#!/usr/bin/env bash

set -e

sudo hostnamectl set-hostname "vm-weewx-wll-test"
yay -Syyuu --noconfirm weewx python-requests

sudo cp -fv /vagrant/testing/conf/weewx.conf /etc/weewx/weewx.conf

export_str="export PATH=\"\$PATH:/vagrant/testing/bin\""

if ! grep -q "$export_str" "/home/vagrant/.bashrc" >/dev/null; then
  echo "$export_str" | sudo tee -a /home/vagrant/.bashrc
fi
if ! grep -q "$export_str" "/home/vagrant/.zshrc" >/dev/null; then
  echo "$export_str" | sudo tee -a /home/vagrant/.zshrc
fi
