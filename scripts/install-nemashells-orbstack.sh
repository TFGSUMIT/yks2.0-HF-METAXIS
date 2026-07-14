#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
MACHINE=${METAXIS_ORBSTACK_MACHINE:-ubuntu}
REVISION=$(git -C "$ROOT" rev-parse --short=12 HEAD 2>/dev/null || printf 'development')
TMP=$(mktemp -d "${TMPDIR:-/tmp}/nemashells.XXXXXX")
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

REMOTE_BASE=".cache/nemashells-bootstrap"
REMOTE_ARCHIVE="${REMOTE_BASE}/$(basename "$ARCHIVE")"
orb -m "$MACHINE" mkdir -p "$REMOTE_BASE"
orb push -m "$MACHINE" "$ARCHIVE" "$REMOTE_BASE/"
orb -m "$MACHINE" sh -lc "rm -rf '${REMOTE_BASE}/source-${REVISION}' && mkdir -p '${REMOTE_BASE}/source-${REVISION}' && tar -xzf '${REMOTE_ARCHIVE}' -C '${REMOTE_BASE}/source-${REVISION}'"
orb -m "$MACHINE" sh "${REMOTE_BASE}/source-${REVISION}/deployment/orbstack/install-guest.sh" "${REMOTE_BASE}/source-${REVISION}" "$REVISION"

printf '%s\n' 'NemaShells installation complete.'
printf '%s\n' "Normal use: orb start ${MACHINE}; orb -m ${MACHINE}; nemashells"
