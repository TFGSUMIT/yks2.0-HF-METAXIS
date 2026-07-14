#!/bin/sh
set -eu

ROLE_ARN=${METAXIS_AWS_ROLE_ARN:?set METAXIS_AWS_ROLE_ARN}
DESTINATION=${1:?usage: bootstrap-bedrock-session.sh OWNER_ONLY_DESTINATION}
PROFILE=${AWS_PROFILE:-default}
REGION=${METAXIS_AWS_REGION:-us-east-1}
USER_NAME=METAXISBedrockBootstrap
POLICY_NAME=AssumeMETAXISBedrockDevelopmentRole

case "$ROLE_ARN" in
  *:role/METAXISBedrockDevelopmentRole) ;;
  *) printf '%s\n' 'METAXIS_AWS_ROLE_ARN is not the registered role.' >&2; exit 1 ;;
esac

CALLER_ARN=$(aws sts get-caller-identity \
  --profile "$PROFILE" \
  --region "$REGION" \
  --query Arn \
  --output text)
case "$CALLER_ARN" in
  *:root) ;;
  *) printf '%s\n' 'Bootstrap requires the authenticated account root session.' >&2; exit 1 ;;
esac

umask 077
mkdir -p "$(dirname -- "$DESTINATION")"
ACCESS_FILE=$(mktemp "${DESTINATION}.access.XXXXXX")
SESSION_FILE=$(mktemp "${DESTINATION}.session.XXXXXX")
ACCESS_KEY_ID=
USER_CREATED=0

cleanup() {
  unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY
  if [ -n "$ACCESS_KEY_ID" ]; then
    aws iam delete-access-key \
      --profile "$PROFILE" \
      --user-name "$USER_NAME" \
      --access-key-id "$ACCESS_KEY_ID" >/dev/null 2>&1 || true
  fi
  if [ "$USER_CREATED" = 1 ]; then
    aws iam delete-user-policy \
      --profile "$PROFILE" \
      --user-name "$USER_NAME" \
      --policy-name "$POLICY_NAME" >/dev/null 2>&1 || true
    aws iam delete-user \
      --profile "$PROFILE" \
      --user-name "$USER_NAME" >/dev/null 2>&1 || true
  fi
  rm -f "$ACCESS_FILE" "$SESSION_FILE"
}
trap cleanup EXIT HUP INT TERM

aws iam create-user \
  --profile "$PROFILE" \
  --user-name "$USER_NAME" \
  --tags Key=yks:product,Value=metaxis Key=yks:purpose,Value=transient-bootstrap \
  >/dev/null
USER_CREATED=1

POLICY_DOCUMENT=$(python3 -c '
import json, sys
print(json.dumps({
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": "sts:AssumeRole",
        "Resource": sys.argv[1],
    }],
}))
' "$ROLE_ARN")
aws iam put-user-policy \
  --profile "$PROFILE" \
  --user-name "$USER_NAME" \
  --policy-name "$POLICY_NAME" \
  --policy-document "$POLICY_DOCUMENT"

aws iam create-access-key \
  --profile "$PROFILE" \
  --user-name "$USER_NAME" \
  --output json >"$ACCESS_FILE"

ACCESS_KEY_ID=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["AccessKey"]["AccessKeyId"])' "$ACCESS_FILE")
AWS_ACCESS_KEY_ID=$ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["AccessKey"]["SecretAccessKey"])' "$ACCESS_FILE")
unset AWS_SESSION_TOKEN
export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY

TEMP_CALLER_ARN=$(AWS_CONFIG_FILE=/dev/null AWS_SHARED_CREDENTIALS_FILE=/dev/null \
  aws sts get-caller-identity \
    --region "$REGION" \
    --query Arn \
    --output text)
case "$TEMP_CALLER_ARN" in
  *:user/METAXISBedrockBootstrap) ;;
  *) printf '%s\n' 'Temporary IAM credentials did not isolate from the root profile.' >&2; exit 1 ;;
esac

attempt=0
while :; do
  if AWS_CONFIG_FILE=/dev/null AWS_SHARED_CREDENTIALS_FILE=/dev/null \
    aws sts assume-role \
    --region "$REGION" \
    --role-arn "$ROLE_ARN" \
    --role-session-name metaxis-protos4-development \
    --duration-seconds 3600 \
    --output json >"$SESSION_FILE"; then
    break
  fi
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 6 ]; then
    printf '%s\n' 'Unable to assume the METAXIS role after IAM propagation retries.' >&2
    exit 1
  fi
  sleep 2
done

python3 -c '
import json, sys
value=json.load(open(sys.argv[1]))
credentials=value["Credentials"]
principal=value["AssumedRoleUser"]["Arn"]
with open(sys.argv[2], "w", encoding="utf-8") as target:
    target.write("[metaxis-bedrock]\n")
    target.write("aws_access_key_id = " + credentials["AccessKeyId"] + "\n")
    target.write("aws_secret_access_key = " + credentials["SecretAccessKey"] + "\n")
    target.write("aws_session_token = " + credentials["SessionToken"] + "\n")
    target.write("x_metaxis_principal_arn = " + principal + "\n")
    target.write("x_metaxis_expiration = " + credentials["Expiration"] + "\n")
' "$SESSION_FILE" "$DESTINATION"
chmod 0600 "$DESTINATION"

cleanup
trap - EXIT HUP INT TERM
printf '%s\n' 'Temporary METAXIS Bedrock role session exported; bootstrap IAM user deleted.'
