#!/usr/bin/env bash

set -e

sudo hostnamectl set-hostname "vm-weewx-wll-test"
sudo pacman -Syyuu --noconfirm

if ! pacman -Qe | cut -f 1 -d " " | grep -q "python-requests"; then
  sudo pacman -S --noconfirm base-devel git wget curl freetype2 python-requests python-objgraph
fi

[[ -d "$HOME/aur/mslx" ]] || git clone https://github.com/michael-slx/aur-packages.git "$HOME/aur/mslx"
[[ -d "$HOME/aur/python-cheetah3" ]] || git clone https://aur.archlinux.org/python-cheetah3.git "$HOME/aur/python-cheetah3"
[[ -d "$HOME/aur/python-pyephem" ]] || git clone https://aur.archlinux.org/python-pyephem.git "$HOME/aur/python-pyephem"

cd "$HOME/aur/python-cheetah3"
git pull
makepkg -si --noconfirm

cd "$HOME/aur/python-pyephem"
git pull
makepkg -si --noconfirm

cd "$HOME/aur/mslx/weewx"
git pull
makepkg -si --noconfirm

sudo cp -fv /vagrant/testing/conf/weewx.conf /etc/weewx/weewx.conf

export_str="export PATH=\"\$PATH:/vagrant/testing/bin\""

if ! grep -q "$export_str" "/home/vagrant/.bashrc" >/dev/null; then
  echo "$export_str" >> /home/vagrant/.bashrc
fi
if ! grep -q "$export_str" "/home/vagrant/.zshrc" >/dev/null; then
  echo "$export_str" >> /home/vagrant/.zshrc
fi
