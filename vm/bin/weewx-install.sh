#!/usr/bin/env bash

set -e

PACKAGES=(
    "weewx"
    "python-pyephem"
    "python-requests"
)

yay -S --noconfirm "${PACKAGES[@]}"
