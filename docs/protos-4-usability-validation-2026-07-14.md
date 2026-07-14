# PROTOS-4 usable conversation validation

Status: passed for a bounded DEVELOPMENT session

Authority: YKS Ops #422, #428, and #474 → #475 → #476

Observed: 2026-07-14

## Delivered behavior

- The Tauri 2 shell lists durable Cloudflare D1 tasks and restores their turns.
- Selecting a task resumes the same thread instead of creating isolated turns.
- METAXIS sends at most 12 prior turns and 24,000 prior characters through the
  provider-neutral brain contract by default.
- The system safety contract remains outside operator content and states the
  DEVELOPMENT, credential, authority, and non-claim boundaries.
- Each model request receives a non-secret live context block that distinguishes
  the active brain route, external inference, D1 application writes, read-only
  credential mounts, GitHub read-only access, and model tool authority.
- Provider failures render as turn-level failures without marking the local
  control plane unhealthy.
- New tasks use the first prompt as their durable display title.

## Live acceptance

The PROTOS-4 workload activated the pinned Amazon Bedrock DEVELOPMENT route:

| Field | Readback |
| --- | --- |
| Route | `aws-bedrock-super-development` |
| Provider model | `nvidia.nemotron-super-3-120b` |
| Source repository | `nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16` |
| Source revision | `d51eab0d1f979ebc26b546e634a04f450d99158e` |
| Runtime | `amazon-bedrock-converse`, `boto3/1.43.47` |
| Session expiry | `2026-07-14T20:20:05Z` |
| Per-request ceiling | `$0.01` |

The synthetic prompt `Reply with exactly: PROTOS-4 LIVE` returned the requested
text. The response recorded 116 input tokens, 7 output tokens, and calculated
cost `$0.00002195`.

The first YKS packet exposed two ambiguous-state errors: it generalized an
earlier deterministic turn's no-model-call statement and confused read-only
credential mounts with D1 application authority. After adding the live context
block, a correction probe reported that the current answer used external
inference and that D1 could append DEVELOPMENT records. It recorded 299 input
tokens, 79 output tokens, and calculated cost `$0.00009620`.

The same thread was recovered after a METAXIS container restart. The D1,
GitHub, and AWS credential files remained read-only container mounts. Their
values were absent from Docker environment metadata, API readback, the model
request, and the D1 turn record.

## Negative proof

A `HIGH/NOFORN` turn returned HTTP 403 with `route_blocked` and `BLOCKED` before
the adapter call. GitHub writes and consequential actions remain denied. The
session does not establish production activation, HIGH/NOFORN eligibility,
model sufficiency, provider availability, or tool-execution authority.

## Billing and shutdown

The route is Bedrock on-demand. It has no standing GPU or endpoint charge, but
each accepted DEVELOPMENT inference is billable. The temporary invocation-only
role session expires automatically. The role can also be removed and the
container returned to mock using the shutdown procedure in
`docs/aws-bedrock-development.md`.
