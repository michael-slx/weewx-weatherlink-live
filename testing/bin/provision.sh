#!/usr/bin/env bash

set -e

sudo hostnamectl set-hostname "vm-weewx-wll-test"
sudo pacman -Syyuu --noconfirm
sudo pacman -S --noconfirm base-devel git wget curl man-pages texinfo python-requests

git clone https://github.com/michael-slx/aur-packages.git "$HOME/aur/mslx"
git clone https://aur.archlinux.org/python-cheetah3.git "$HOME/aur/python-cheetah3"

cd "$HOME/aur/python-cheetah3"
makepkg -si --noconfirm

cd "$HOME/aur/mslx/python-ephem"
makepkg -si --noconfirm

cd "$HOME/aur/mslx/weewx"
makepkg -si --noconfirm

sudo cp -Rsfv /vagrant/bin/user /usr/lib/weewx
sudo cp -fv /vagrant/testing/conf/weewx.conf /etc/weewx/weewx.conf

echo 'export PATH=$PATH:/vagrant/testing/bin' | tee /home/vagrant/.bashrc >/dev/null
echo 'export PATH=$PATH:/vagrant/testing/bin' | tee /home/vagrant/.zshrc >/dev/null
