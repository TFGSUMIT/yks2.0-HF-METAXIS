#!/bin/sh
set -eu

SOURCE_DIR=${1:?usage: install-guest.sh SOURCE_DIR}

sudo install -m 0755 "$SOURCE_DIR/deployment/orbstack/nemashells" /usr/local/bin/nemashells
printf '%s\n' 'NemaShells guest launcher installed.'
