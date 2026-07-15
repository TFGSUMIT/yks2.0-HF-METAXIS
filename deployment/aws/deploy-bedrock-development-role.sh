#!/bin/sh
set -eu

REGION=${METAXIS_AWS_REGION:-us-east-1}
PROFILE=${AWS_PROFILE:-default}
PRINCIPAL=${METAXIS_AWS_BOOTSTRAP_PRINCIPAL_ARN:?set METAXIS_AWS_BOOTSTRAP_PRINCIPAL_ARN}
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)

aws cloudformation deploy \
  --profile "$PROFILE" \
  --region "$REGION" \
  --stack-name metaxis-bedrock-development \
  --template-file "$ROOT/deployment/aws/bedrock-development-role.yaml" \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides "TrustedPrincipalArn=$PRINCIPAL" \
  --tags yks:product=metaxis yks:authority=474-475-476

aws cloudformation describe-stacks \
  --profile "$PROFILE" \
  --region "$REGION" \
  --stack-name metaxis-bedrock-development \
  --query 'Stacks[0].Outputs[?OutputKey==`RoleArn`].OutputValue' \
  --output text
