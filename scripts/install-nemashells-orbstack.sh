#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
MACHINE=${METAXIS_ORBSTACK_MACHINE:-PROTOS-3}
REVISION=$(git -C "$ROOT" rev-parse --short=12 HEAD 2>/dev/null || printf 'development')
command -v orb >/dev/null 2>&1 || {
  printf '%s\n' 'OrbStack command `orb` is required.' >&2
  exit 1
}
command -v docker >/dev/null 2>&1 || {
  printf '%s\n' 'OrbStack-managed Docker command `docker` is required.' >&2
  exit 1
}

APP=$("$ROOT/scripts/build-nemashells-app.sh")
mkdir -p "$HOME/Applications"
rm -rf "$HOME/Applications/NemaShells.app"
ditto "$APP" "$HOME/Applications/NemaShells.app"

orb start "$MACHINE" >/dev/null

docker build --build-arg "METAXIS_REVISION=${REVISION}" --tag "metaxis:${REVISION}" "$ROOT"
docker rm -f nemashells-metaxis >/dev/null 2>&1 || true
set -- docker run -d \
  --name nemashells-metaxis \
  --restart unless-stopped \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  --cap-drop ALL \
  --security-opt no-new-privileges:true \
  --pids-limit 128 \
  --memory 512m \
  --publish 127.0.0.1:4310:4310 \
  --env METAXIS_PROFILE=orbstack-development \
  --env METAXIS_DATA_CLASSIFICATION=DEVELOPMENT \
  --env METAXIS_EXTERNAL_MODEL_CALLS=0 \
  --env METAXIS_EXTERNAL_TELEMETRY=0 \
  --env "METAXIS_OPERATOR_CADENCE=5.6 sol" \
  --env "METAXIS_GITHUB_ACCOUNT=${METAXIS_GITHUB_ACCOUNT:-LittleYeti-Dev}" \
  --env "METAXIS_SOURCE_REPO=${METAXIS_SOURCE_REPO:-LittleYeti-Dev/yks2.0-ops-hub}" \
  --env "METAXIS_TARGET_REPO=${METAXIS_TARGET_REPO:-LittleYeti-Dev/yks2.0-HF-METAXIS}" \
  --env "METAXIS_STATE_BACKEND=${METAXIS_STATE_BACKEND:-memory}" \
  --env "CLOUDFLARE_ACCOUNT_ID=${CLOUDFLARE_ACCOUNT_ID:-}" \
  --env "METAXIS_D1_DATABASE_ID=${METAXIS_D1_DATABASE_ID:-}" \
  --env "CLOUDFLARE_D1_API_TOKEN=${CLOUDFLARE_D1_API_TOKEN:-}" \
  --env "METAXIS_D1_TIMEOUT_SECONDS=${METAXIS_D1_TIMEOUT_SECONDS:-10}" \
  --env "METAXIS_D1_API_BASE=${METAXIS_D1_API_BASE:-https://api.cloudflare.com/client/v4}"

if [ -n "${METAXIS_GITHUB_TOKEN_FILE:-}" ]; then
  test -f "$METAXIS_GITHUB_TOKEN_FILE" || {
    printf '%s\n' 'METAXIS_GITHUB_TOKEN_FILE is not a regular file.' >&2
    exit 1
  }
  set -- "$@" \
    --mount "type=bind,src=${METAXIS_GITHUB_TOKEN_FILE},dst=/run/secrets/metaxis_github_token,readonly" \
    --env METAXIS_GITHUB_TOKEN_FILE=/run/secrets/metaxis_github_token
fi

"$@" "metaxis:${REVISION}" >/dev/null

orb -m "$MACHINE" sh "$ROOT/deployment/orbstack/install-guest.sh" "$ROOT"

attempt=0
while ! curl --fail --silent --show-error http://127.0.0.1:4310/healthz >/dev/null 2>&1; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 40 ]; then
    docker logs nemashells-metaxis >&2 || true
    exit 1
  fi
  sleep 0.25
done

orb -m "$MACHINE" curl --fail --silent --show-error http://host.internal:4310/healthz >/dev/null

printf '%s\n' 'NemaShells installation complete.'
printf '%s\n' "Normal use: orb start ${MACHINE}; orb -m ${MACHINE}; nemashells"
