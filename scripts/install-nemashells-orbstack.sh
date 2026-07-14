#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
MACHINE=${METAXIS_ORBSTACK_MACHINE:-ubuntu}
REVISION=$(git -C "$ROOT" rev-parse --short=12 HEAD 2>/dev/null || printf 'development')
mkdir -p "$ROOT/.build"
TMP=$(mktemp -d "$ROOT/.build/nemashells-bootstrap.XXXXXX")
trap 'rm -rf "$TMP"' EXIT HUP INT TERM

command -v orb >/dev/null 2>&1 || {
  printf '%s\n' 'OrbStack command `orb` is required.' >&2
  exit 1
}

APP=$("$ROOT/scripts/build-nemashells-app.sh")
mkdir -p "$HOME/Applications"
rm -rf "$HOME/Applications/NemaShells.app"
ditto "$APP" "$HOME/Applications/NemaShells.app"

orb start "$MACHINE" >/dev/null

ARCHIVE="$TMP/metaxis-${REVISION}.tar.gz"
tar -C "$ROOT" \
  --exclude=.git \
  --exclude=.venv \
  --exclude=.build \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude=.env \
  -czf "$ARCHIVE" .

REMOTE_ARCHIVE="/var/tmp/$(basename "$ARCHIVE")"
REMOTE_SOURCE="/var/tmp/nemashells-source-${REVISION}"
orb -m "$MACHINE" sh -lc "rm -rf '${REMOTE_SOURCE}' && mkdir -p '${REMOTE_SOURCE}' && cp '${ARCHIVE}' '${REMOTE_ARCHIVE}' && tar -xzf '${REMOTE_ARCHIVE}' -C '${REMOTE_SOURCE}'"
orb -m "$MACHINE" sh "${REMOTE_SOURCE}/deployment/orbstack/install-guest.sh" "$REMOTE_SOURCE" "$REVISION"
orb -m "$MACHINE" sh -lc "rm -rf '${REMOTE_SOURCE}' '${REMOTE_ARCHIVE}'"

printf '%s\n' 'NemaShells installation complete.'
printf '%s\n' "Normal use: orb start ${MACHINE}; orb -m ${MACHINE}; nemashells"
