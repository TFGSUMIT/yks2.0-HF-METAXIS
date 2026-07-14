#!/bin/sh
set -eu

ROLE_ARN=${METAXIS_AWS_ROLE_ARN:?set METAXIS_AWS_ROLE_ARN}
DESTINATION=${1:?usage: export-bedrock-session.sh OWNER_ONLY_DESTINATION}
PROFILE=${AWS_PROFILE:-default}
REGION=${METAXIS_AWS_REGION:-us-east-1}

case "$ROLE_ARN" in
  *:role/METAXISBedrockDevelopmentRole) ;;
  *) printf '%s\n' 'METAXIS_AWS_ROLE_ARN is not the registered role.' >&2; exit 1 ;;
esac

umask 077
mkdir -p "$(dirname -- "$DESTINATION")"
temporary=$(mktemp "${DESTINATION}.XXXXXX")
trap 'rm -f "$temporary"' EXIT HUP INT TERM

aws sts assume-role \
  --profile "$PROFILE" \
  --region "$REGION" \
  --role-arn "$ROLE_ARN" \
  --role-session-name metaxis-protos4-development \
  --duration-seconds 3600 \
  --output json |
python3 -c '
import json, sys
value=json.load(sys.stdin)
credentials=value["Credentials"]
principal=value["AssumedRoleUser"]["Arn"]
print("[metaxis-bedrock]")
print("aws_access_key_id = " + credentials["AccessKeyId"])
print("aws_secret_access_key = " + credentials["SecretAccessKey"])
print("aws_session_token = " + credentials["SessionToken"])
print("x_metaxis_principal_arn = " + principal)
print("x_metaxis_expiration = " + credentials["Expiration"])
' >"$temporary"

chmod 0600 "$temporary"
mv "$temporary" "$DESTINATION"
trap - EXIT HUP INT TERM
printf '%s\n' 'Temporary METAXIS Bedrock role session exported.'
