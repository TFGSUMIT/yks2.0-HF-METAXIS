# NemaShells functional prototype activation

Status: installation complete; live integrations gated  
Authority: YKS Ops #422, #423, and #474 → #475 → #476  
Observed: 2026-07-14

## Definition of functional prototype

The prototype is functional when the operator can start `PROTOS-4`, log in,
run `yetis live`, exchange a DEVELOPMENT-classified turn with an approved
inference endpoint, restart the METAXIS container, and recover the thread from
Cloudflare D1. GitHub metadata readback must identify the authority and
implementation repositories without granting GitHub write access.

This definition does not satisfy the HIGH/NOFORN deployment gate. The laptop
profile remains DEVELOPMENT-only even after all three live integrations pass.

## Current readback

| Surface | Current state | Activation result required |
| --- | --- | --- |
| Installed Tauri 2 shell | Running through `PROTOS-4`; loopback-only | Retain health-gated `yetis live` boot |
| GitHub | Declared metadata only; no credential; writes denied | Live bounded read of `yks2.0-ops-hub` and `yks2.0-HF-METAXIS` |
| Brain | `mock-local-development`; external calls disabled | One approved DEVELOPMENT turn through the pinned endpoint route |
| Candidate | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` at `cbd3fa9f933d55ef16a84236559f4ee2a0526848` | Preserve repository and revision in response provenance |
| Hugging Face endpoint | Not created; spend cap `$0` | Operator-approved endpoint configuration and explicit spend ceiling |
| Dynamic storage | `memory-development`; not durable | D1 migration applied and restart/recovery proof captured |
| HIGH/NOFORN | Blocked | Remains blocked; prototype activation does not change this row |

## Gate 1 — GitHub metadata read

1. Create a fine-grained token selected only for
   `LittleYeti-Dev/yks2.0-ops-hub` and
   `LittleYeti-Dev/yks2.0-HF-METAXIS` with repository Metadata read access.
2. Store it outside the repository in an owner-only file (`0600`).
3. Set `METAXIS_GITHUB_TOKEN_FILE` to that host path and reinstall/restart the
   OrbStack workload. The installer mounts it read-only.
4. Confirm `/api/v1/github-state` reports `live: true`, both repositories, and
   `writes_allowed: false`.
5. Confirm the prompt `what gh are you talking to` uses
   `github-readback-local`, not the model route.

The broker deliberately ignores broad `GH_TOKEN` and `GITHUB_TOKEN` values.

## Gate 2 — DEVELOPMENT inference

This gate is billable and must not start until the operator accepts the
endpoint size, region, autoscaling bounds, idle behavior, and spend ceiling.

1. Create the dedicated Hugging Face Inference Endpoint from the pinned
   candidate revision; do not use a floating branch.
2. Record the endpoint runtime image/version and the effective license and
   data-handling terms in the provider evidence.
3. Create a separate inference-only runtime token. Do not mount the existing
   endpoint-management token into METAXIS.
4. Store the runtime token in an owner-only file outside the repository and set
   `METAXIS_BRAIN_API_KEY_FILE` to its path.
5. Set `METAXIS_BRAIN_MODE=openai-compatible`, the registered endpoint URL and
   route metadata, then set `METAXIS_EXTERNAL_MODEL_CALLS=1` last.
6. Run a synthetic/public prompt. Verify model repository, immutable revision,
   route, latency, token usage, and error evidence in the response.
7. Re-run a HIGH/NOFORN request and verify denial occurs before network I/O.

If any endpoint coordinate, credential, custody flag, or route gate is absent,
METAXIS stays on the deterministic mock or denies the route.

## Gate 3 — Cloudflare D1 durability

1. Select the approved Cloudflare account and create the
   `metaxis-dynamic-state` D1 database.
2. Create a least-privilege D1 Read/Write token and store it in an owner-only
   file outside the repository.
3. Apply
   `deployment/cloudflare/d1/migrations/0001_metaxis_dynamic_state.sql` to the
   named remote database and capture the migration readback.
4. Set the non-secret account/database coordinates,
   `CLOUDFLARE_D1_API_TOKEN_FILE`, and finally
   `METAXIS_STATE_BACKEND=cloudflare-d1`.
5. Create a DEVELOPMENT thread and turn, restart the container, and verify the
   same thread and turn are recovered.
6. Verify the D1 token is absent from Docker environment inspection, API
   responses, logs, model requests, and stored rows.

Selecting D1 with an incomplete or insecure token-file configuration fails
startup. It never falls back silently to memory.

## Acceptance evidence

Attach the following to the existing SAFe task chain; do not create orphan
issues:

- commit and immutable container tag;
- redacted operator-state and GitHub-state responses;
- one successful DEVELOPMENT inference provenance record;
- one pre-network HIGH/NOFORN denial;
- D1 migration list and restart/recovery proof;
- endpoint configuration and accepted spend ceiling; and
- test/build results with explicit nonclaims.
