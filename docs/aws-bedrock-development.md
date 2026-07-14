# AWS Bedrock DEVELOPMENT route

Status: discovered / not activated  
Authority: YKS Ops #422, #423, and #474 → #475 → #476  
Observed: 2026-07-14

The AWS account exposes NVIDIA Nemotron 3 Super 120B A12B as ON_DEMAND model
`nvidia.nemotron-super-3-120b` in `us-east-1`. It also exposes versioned
comparison model `openai.gpt-oss-120b-1:0`. No SageMaker endpoint exists and
no GPU instance was created for this route.

The primary source-weight evidence is pinned to
`nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16` revision
`d51eab0d1f979ebc26b546e634a04f450d99158e`, under the NVIDIA Nemotron Open
Model License. The comparison source is `openai/gpt-oss-120b` revision
`b5c939de8f754692c1647ca79fbf85e8c1e70f8a`, under Apache-2.0.

## Availability posture

Bedrock ON_DEMAND is the primary DEVELOPMENT route because it avoids standing
GPU cost. The account did not advertise a system-defined U.S. cross-region
inference profile for either candidate at observation time. METAXIS therefore
must fail closed on provider errors and may switch to the comparison model only
through an explicit DEVELOPMENT route decision.

A Hugging Face dedicated Super endpoint is retained as a cold availability
option, not an automatic fallback. The pinned BF16 model card states a minimum
of eight H100-80GB GPUs, so its capacity and spend require separate acceptance.

## Credential boundary

The discovery login used temporary root console credentials. Root credentials
are prohibited from METAXIS. Runtime activation requires an assumable role
limited to the selected Bedrock model invocation actions, a short session, an
owner-only temporary credentials file outside the repository, and a read-only
container mount. The credential is never included in prompts, responses,
thread state, D1, evidence payloads, or the Tauri shell.

## Non-claims

Neither model has been invoked or evaluated by METAXIS. This profile is
synthetic/public DEVELOPMENT only. It does not establish HIGH/NOFORN
eligibility, U.S.-person-only administration, production availability, or a
provider SLA.
