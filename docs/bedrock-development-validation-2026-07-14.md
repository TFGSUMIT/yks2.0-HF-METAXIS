# Bedrock Super controlled DEVELOPMENT validation

Authority: YKS Ops #422, #423, and #474 → #475 → #476

Timestamp: `2026-07-14T18:38:02.674426+00:00`

## Immutable runtime

- Git commit: `6428ddaab6f34eb4c1f3a7dcf170980116ce19aa`
- Container tag: `metaxis:6428dda`
- Local image ID:
  `sha256:86beb1b2d4634435f9983bcc14ac091ba08a2bb068ac2a81d66a230c5c9cb4e1`
- Provider: `aws-bedrock`
- Region: `us-east-1`
- Bedrock model: `nvidia.nemotron-super-3-120b`
- Source repository: `nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16`
- Source revision: `d51eab0d1f979ebc26b546e634a04f450d99158e`
- Runtime: `amazon-bedrock-converse`, `boto3/1.43.47`

## Input and result

The input was synthetic DEVELOPMENT data and requested one fixed phrase. No
private, operational, controlled, HIGH, or NOFORN data was sent.

- Route: `aws-bedrock-super-development`
- Exact response: `YETI BEDROCK LIVE`
- Input tokens: `38`
- Output tokens: `9`
- Calculated usage cost: `$0.00001155`
- Configured maximum estimated request cost: `$0.001`

The response included provider, source repository, immutable revision,
runtime, runtime version, token usage, calculated cost, and route in the
METAXIS `brain_evidence` record.

## Credential and spend boundary

- CloudFormation created a named role limited to Bedrock invocation of the
  exact Super model.
- Root credentials were never mounted into METAXIS.
- A transient bootstrap IAM user held only permission to assume that exact
  role; its access key, inline policy, and user were deleted immediately after
  the one-hour role session was issued.
- The owner-only session file was mounted read-only for the validation.
- The adapter enforced classification, input, output, and estimated-cost gates
  before network I/O.

## Verified shutdown

After the successful turn:

- PROTOS-4 returned to `mock-local-development`;
- `METAXIS_EXTERNAL_MODEL_CALLS` returned to `0`;
- HIGH/NOFORN remained `BLOCKED`;
- the AWS credential mount was absent from the replacement container;
- the owner-only role-session file was deleted;
- the `metaxis-bedrock-development` CloudFormation stack deletion completed;
- the AWS CLI root login cache was cleared; and
- the GitHub broker remained metadata-read-only.

Bedrock has no persistent billing toggle. These controls prevent new METAXIS
invocations; already incurred usage can appear later in AWS billing reports.

## Non-claims

This is one connectivity and contract proof, not a quality, safety, load,
availability, durability, failover, or production evaluation. It does not
activate the comparator model, Hugging Face capacity, D1, consequential tools,
or HIGH/NOFORN processing.
