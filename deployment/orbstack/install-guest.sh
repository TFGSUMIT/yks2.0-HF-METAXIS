#!/bin/sh
set -eu

SOURCE_DIR=${1:?usage: install-guest.sh SOURCE_DIR}

sudo install -m 0755 "$SOURCE_DIR/deployment/orbstack/nemashells" /usr/local/bin/nemashells
sudo install -m 0755 "$SOURCE_DIR/deployment/orbstack/nemashells-tauri" /usr/local/bin/nemashells-tauri
sudo install -m 0755 "$SOURCE_DIR/deployment/orbstack/yetis" /usr/local/bin/yetis
sudo ln -sfn /usr/local/bin/yetis /usr/local/bin/yeti
sudo ln -sfn /usr/local/bin/yetis /usr/local/bin/yetis-live
sudo ln -sfn /usr/local/bin/yetis /usr/local/bin/yeti-live
printf '%s\n' 'NemaShells Swift, Tauri, and Yeti live guest launchers installed.'
