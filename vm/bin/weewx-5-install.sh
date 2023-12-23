#!/usr/bin/env bash

set -e

SRC_DIR="$HOME/weewx"
REPO_URL="https://github.com/weewx/weewx.git"
REPO_BRANCH="V5"

if [[ ! -d "$SRC_DIR" ]]; then
    git clone "$REPO_URL" "$SRC_DIR" -b "$REPO_BRANCH"
    pushd "$SRC_DIR"
else
    pushd "$SRC_DIR"
    git restore .
    git clean -xdf
    git pull origin
fi

python -m venv ./venv
. ./venv/bin/activate
pip install poetry mkdocs mkdocs-material pymdown-extensions
make pypi-package
deactivate

pipx install $SRC_DIR/dist/weewx-5.*.whl
pipx inject weewx requests
