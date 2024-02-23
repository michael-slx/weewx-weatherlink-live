#!/usr/bin/env bash

set -e

SRC_DIR="$HOME/weewx"
REPO_URL="https://github.com/weewx/weewx.git"
REPO_BRANCH="master"

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
make pypi-package
deactivate

pipx install $SRC_DIR/dist/weewx-5.*.whl
pipx inject weewx requests

weectl station create $HOME/weewx-data --no-prompt
