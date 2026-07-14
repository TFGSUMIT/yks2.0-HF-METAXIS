#!/bin/sh
set -eu

SOURCE_DIR=${1:?usage: install-guest.sh SOURCE_DIR}

sudo install -m 0755 "$SOURCE_DIR/deployment/orbstack/nemashells" /usr/local/bin/nemashells
sudo install -m 0755 "$SOURCE_DIR/deployment/orbstack/nemashells-tauri" /usr/local/bin/nemashells-tauri
sudo install -m 0755 "$SOURCE_DIR/deployment/orbstack/yetis" /usr/local/bin/yetis
sudo install -m 0755 "$SOURCE_DIR/deployment/orbstack/metaxis-capabilities" /usr/local/bin/metaxis-capabilities
sudo ln -sfn /usr/local/bin/yetis /usr/local/bin/yeti
sudo ln -sfn /usr/local/bin/yetis /usr/local/bin/yetis-live
sudo ln -sfn /usr/local/bin/yetis /usr/local/bin/yeti-live
sudo install -d -m 0755 /etc/metaxis/capabilities/skills/yeti-boot
sudo install -m 0644 "$SOURCE_DIR/src/metaxis/capabilities/protos-4.json" /etc/metaxis/capabilities/protos-4.json
sudo install -m 0644 "$SOURCE_DIR/src/metaxis/capabilities/skills/yeti-boot/SKILL.md" /etc/metaxis/capabilities/skills/yeti-boot/SKILL.md
printf '%s\n' 'NemaShells launchers and the PROTOS-4 capability pack are installed.'
metaxis-capabilities
