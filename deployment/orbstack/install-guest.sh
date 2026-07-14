#!/bin/sh
set -eu

SOURCE_DIR=${1:?usage: install-guest.sh SOURCE_DIR}

sudo install -m 0755 "$SOURCE_DIR/deployment/orbstack/nemashells" /usr/local/bin/nemashells
sudo install -m 0755 "$SOURCE_DIR/deployment/orbstack/nemashells-tauri" /usr/local/bin/nemashells-tauri
printf '%s\n' 'NemaShells Swift and Tauri guest launchers installed.'
