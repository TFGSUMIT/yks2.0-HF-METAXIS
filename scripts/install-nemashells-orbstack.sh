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
  --env "METAXIS_EXTERNAL_MODEL_CALLS=${METAXIS_EXTERNAL_MODEL_CALLS:-0}" \
  --env METAXIS_EXTERNAL_TELEMETRY=0 \
  --env "METAXIS_OPERATOR_CADENCE=5.6 sol" \
  --env "METAXIS_GITHUB_ACCOUNT=${METAXIS_GITHUB_ACCOUNT:-LittleYeti-Dev}" \
  --env "METAXIS_SOURCE_REPO=${METAXIS_SOURCE_REPO:-LittleYeti-Dev/yks2.0-ops-hub}" \
  --env "METAXIS_TARGET_REPO=${METAXIS_TARGET_REPO:-LittleYeti-Dev/yks2.0-HF-METAXIS}" \
  --env "METAXIS_STATE_BACKEND=${METAXIS_STATE_BACKEND:-memory}" \
  --env "CLOUDFLARE_ACCOUNT_ID=${CLOUDFLARE_ACCOUNT_ID:-}" \
  --env "METAXIS_D1_DATABASE_ID=${METAXIS_D1_DATABASE_ID:-}" \
  --env "METAXIS_D1_TIMEOUT_SECONDS=${METAXIS_D1_TIMEOUT_SECONDS:-10}" \
  --env "METAXIS_D1_API_BASE=${METAXIS_D1_API_BASE:-https://api.cloudflare.com/client/v4}" \
  --env "METAXIS_BRAIN_MODE=${METAXIS_BRAIN_MODE:-mock}" \
  --env "METAXIS_BRAIN_URL=${METAXIS_BRAIN_URL:-}" \
  --env "METAXIS_BRAIN_PROVIDER=${METAXIS_BRAIN_PROVIDER:-}" \
  --env "METAXIS_BRAIN_ROUTE_ID=${METAXIS_BRAIN_ROUTE_ID:-}" \
  --env "METAXIS_BRAIN_MODEL=${METAXIS_BRAIN_MODEL:-nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16}" \
  --env "METAXIS_BRAIN_REVISION=${METAXIS_BRAIN_REVISION:-d51eab0d1f979ebc26b546e634a04f450d99158e}" \
  --env "METAXIS_BRAIN_DEVELOPER_COUNTRY=${METAXIS_BRAIN_DEVELOPER_COUNTRY:-US}" \
  --env "METAXIS_BRAIN_PLACEMENT=${METAXIS_BRAIN_PLACEMENT:-}" \
  --env "METAXIS_BRAIN_MAX_OUTPUT_TOKENS=${METAXIS_BRAIN_MAX_OUTPUT_TOKENS:-4096}" \
  --env "METAXIS_BRAIN_MAX_INPUT_CHARS=${METAXIS_BRAIN_MAX_INPUT_CHARS:-100000}" \
  --env "METAXIS_BRAIN_MAX_REQUEST_COST_USD=${METAXIS_BRAIN_MAX_REQUEST_COST_USD:-0.01}" \
  --env "METAXIS_BRAIN_TIMEOUT_SECONDS=${METAXIS_BRAIN_TIMEOUT_SECONDS:-60}" \
  --env "METAXIS_BRAIN_CONTEXT_TURNS=${METAXIS_BRAIN_CONTEXT_TURNS:-12}" \
  --env "METAXIS_BRAIN_CONTEXT_CHARS=${METAXIS_BRAIN_CONTEXT_CHARS:-24000}" \
  --env "METAXIS_VERIFICATION_MAX_ATTEMPTS=${METAXIS_VERIFICATION_MAX_ATTEMPTS:-2}" \
  --env "METAXIS_VERIFICATION_MAX_OUTPUT_TOKENS=${METAXIS_VERIFICATION_MAX_OUTPUT_TOKENS:-1024}" \
  --env "METAXIS_AWS_REGION=${METAXIS_AWS_REGION:-us-east-1}" \
  --env "METAXIS_BEDROCK_MODEL_ID=${METAXIS_BEDROCK_MODEL_ID:-nvidia.nemotron-super-3-120b}" \
  --env "METAXIS_BRAIN_US_PERSON_ADMIN_ONLY=${METAXIS_BRAIN_US_PERSON_ADMIN_ONLY:-0}" \
  --env "METAXIS_BRAIN_US_PERSON_USER_ONLY=${METAXIS_BRAIN_US_PERSON_USER_ONLY:-0}" \
  --env "METAXIS_BRAIN_US_LOCATION_ONLY=${METAXIS_BRAIN_US_LOCATION_ONLY:-0}" \
  --env "METAXIS_BRAIN_EGRESS_DEFAULT_DENY=${METAXIS_BRAIN_EGRESS_DEFAULT_DENY:-0}" \
  --env "METAXIS_BRAIN_EXTERNAL_TELEMETRY_DISABLED=${METAXIS_BRAIN_EXTERNAL_TELEMETRY_DISABLED:-0}" \
  --env "METAXIS_BRAIN_CUSTODY_APPROVED=${METAXIS_BRAIN_CUSTODY_APPROVED:-0}" \
  --env "METAXIS_HIGH_NOFORN_AUTHORITY_RECORD=${METAXIS_HIGH_NOFORN_AUTHORITY_RECORD:-}"

if [ -n "${CLOUDFLARE_D1_API_TOKEN:-}" ]; then
  printf '%s\n' 'OrbStack deployment rejects CLOUDFLARE_D1_API_TOKEN; use CLOUDFLARE_D1_API_TOKEN_FILE.' >&2
  exit 1
fi
if [ -n "${METAXIS_BRAIN_API_KEY:-}" ]; then
  printf '%s\n' 'OrbStack deployment rejects METAXIS_BRAIN_API_KEY; use METAXIS_BRAIN_API_KEY_FILE.' >&2
  exit 1
fi
if [ -n "${AWS_ACCESS_KEY_ID:-}" ] || [ -n "${AWS_SECRET_ACCESS_KEY:-}" ] || [ -n "${AWS_SESSION_TOKEN:-}" ]; then
  printf '%s\n' 'OrbStack deployment rejects direct AWS credential variables; use METAXIS_AWS_CREDENTIALS_FILE.' >&2
  exit 1
fi

if [ -n "${METAXIS_GITHUB_TOKEN_FILE:-}" ]; then
  test -f "$METAXIS_GITHUB_TOKEN_FILE" || {
    printf '%s\n' 'METAXIS_GITHUB_TOKEN_FILE is not a regular file.' >&2
    exit 1
  }
  set -- "$@" \
    --mount "type=bind,src=${METAXIS_GITHUB_TOKEN_FILE},dst=/run/secrets/metaxis_github_token,readonly" \
    --env METAXIS_GITHUB_TOKEN_FILE=/run/secrets/metaxis_github_token
fi

if [ -n "${CLOUDFLARE_D1_API_TOKEN_FILE:-}" ]; then
  test -f "$CLOUDFLARE_D1_API_TOKEN_FILE" || {
    printf '%s\n' 'CLOUDFLARE_D1_API_TOKEN_FILE is not a regular file.' >&2
    exit 1
  }
  set -- "$@" \
    --mount "type=bind,src=${CLOUDFLARE_D1_API_TOKEN_FILE},dst=/run/secrets/metaxis_d1_token,readonly" \
    --env CLOUDFLARE_D1_API_TOKEN_FILE=/run/secrets/metaxis_d1_token
fi

if [ -n "${METAXIS_BRAIN_API_KEY_FILE:-}" ]; then
  test -f "$METAXIS_BRAIN_API_KEY_FILE" || {
    printf '%s\n' 'METAXIS_BRAIN_API_KEY_FILE is not a regular file.' >&2
    exit 1
  }
  set -- "$@" \
    --mount "type=bind,src=${METAXIS_BRAIN_API_KEY_FILE},dst=/run/secrets/metaxis_brain_api_key,readonly" \
    --env METAXIS_BRAIN_API_KEY_FILE=/run/secrets/metaxis_brain_api_key
fi

if [ "${METAXIS_BRAIN_MODE:-mock}" = "aws-bedrock" ]; then
  test -n "${METAXIS_AWS_CREDENTIALS_FILE:-}" || {
    printf '%s\n' 'aws-bedrock mode requires METAXIS_AWS_CREDENTIALS_FILE.' >&2
    exit 1
  }
  test -f "$METAXIS_AWS_CREDENTIALS_FILE" || {
    printf '%s\n' 'METAXIS_AWS_CREDENTIALS_FILE is not a regular file.' >&2
    exit 1
  }
  set -- "$@" \
    --mount "type=bind,src=${METAXIS_AWS_CREDENTIALS_FILE},dst=/run/secrets/metaxis_aws_credentials,readonly" \
    --env METAXIS_AWS_CREDENTIALS_FILE=/run/secrets/metaxis_aws_credentials
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
