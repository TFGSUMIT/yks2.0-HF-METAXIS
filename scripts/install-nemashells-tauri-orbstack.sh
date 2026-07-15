#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PACKAGE="$ROOT/apps/nemashells-tauri"
MACHINE=${METAXIS_TAURI_ORBSTACK_MACHINE:-PROTOS-4}

command -v pnpm >/dev/null 2>&1 || {
  printf '%s\n' 'pnpm is required to build the Tauri frontend.' >&2
  exit 1
}
command -v cargo >/dev/null 2>&1 || {
  printf '%s\n' 'Rust/Cargo is required to build Tauri 2.' >&2
  exit 1
}
command -v orb >/dev/null 2>&1 || {
  printf '%s\n' 'OrbStack command `orb` is required.' >&2
  exit 1
}

pnpm --dir "$PACKAGE" install --frozen-lockfile
pnpm --dir "$PACKAGE" tauri build --bundles app

APP="$PACKAGE/src-tauri/target/release/bundle/macos/NemaShells Tauri.app"
test -d "$APP" || {
  printf '%s\n' "Tauri bundle was not found at $APP" >&2
  exit 1
}

mkdir -p "$HOME/Applications"
rm -rf "$HOME/Applications/NemaShells Tauri.app"
ditto "$APP" "$HOME/Applications/NemaShells Tauri.app"

orb start "$MACHINE" >/dev/null
orb -m "$MACHINE" sh "$ROOT/deployment/orbstack/install-guest.sh" "$ROOT"
orb -m "$MACHINE" curl --fail --silent --show-error http://host.internal:4310/healthz >/dev/null

printf '%s\n' 'NemaShells Tauri installation complete.'
printf '%s\n' "Normal use: orb start ${MACHINE}; orb -m ${MACHINE}; yetis live"
