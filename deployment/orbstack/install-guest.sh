#!/bin/sh
set -eu

SOURCE_DIR=${1:?usage: install-guest.sh SOURCE_DIR [REVISION]}
REVISION=${2:-development}
RELEASE_DIR="/opt/metaxis/releases/${REVISION}"
IMAGE="metaxis/nemashells:${REVISION}"

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends docker.io curl ca-certificates
sudo systemctl enable --now docker.service

sudo install -d -m 0755 "$RELEASE_DIR" /etc/metaxis
sudo cp -R "${SOURCE_DIR}/." "$RELEASE_DIR/"
sudo docker build --build-arg "METAXIS_REVISION=${REVISION}" --tag "$IMAGE" "$RELEASE_DIR"

sudo install -m 0644 "$RELEASE_DIR/deployment/systemd/nemashells.service" /etc/systemd/system/nemashells.service
sudo install -m 0755 "$RELEASE_DIR/deployment/orbstack/nemashells" /usr/local/bin/nemashells
printf 'METAXIS_IMAGE=%s\nMETAXIS_PROFILE=orbstack-development\n' "$IMAGE" \
  | sudo tee /etc/metaxis/nemashells.env >/dev/null

sudo systemctl daemon-reload
sudo systemctl enable --now nemashells.service

attempt=0
while ! curl --fail --silent --show-error http://127.0.0.1:4310/healthz >/dev/null 2>&1; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 40 ]; then
    sudo systemctl --no-pager --full status nemashells.service || true
    exit 1
  fi
  sleep 0.25
done

printf '%s\n' "NemaShells service installed: ${IMAGE}"
curl --fail --silent --show-error http://127.0.0.1:4310/api/v1/operator-state
printf '\n'
