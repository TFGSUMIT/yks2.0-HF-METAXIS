# NemaShells functional prototype activation

Status: all three functional-prototype gates passed; DEVELOPMENT only

Sunset: the PROTOS-4/Tauri validation path was stopped and retired by operator
ruling on 2026-07-15. The results below remain historical proof; forward
NemaShells delivery does not depend on PROTOS-4 or Tauri.

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

## Usable PROTOS-4 conversation contract

The installed Tauri shell lists durable D1 tasks, restores their turns after
restart, and sends a bounded window of prior DEVELOPMENT turns through the
provider-neutral brain contract. The default window is 12 turns or 24,000
characters, whichever is reached first. The Bedrock adapter independently
enforces its registered input, output-token, and per-request cost ceilings.

The model receives only the system safety contract and thread conversation. It
does not receive the D1, GitHub, or AWS credential; raw adapter configuration;
Docker metadata; or action authority. A provider failure appears as a safe
turn-level error and does not mark the local control plane unhealthy.

The native PROTOS-3 NemaShells surface is now the preferred operator shell.
External turns pass through the structured repair loop documented in
`docs/architecture/self-correction-harness.md`. Registered facts are rendered
deterministically; free-form model synthesis is withheld until a semantic
verifier is separately evaluated. Verification and aggregate brain evidence
are durable D1 turn fields.

## Current readback

| Surface | Current state | Activation result required |
| --- | --- | --- |
| Installed native shell | NemaShells running through `PROTOS-3`; loopback-only | Retain health-gated `nemashells` boot; Tauri remains a secondary lane |
| Capability pack | `yeti-boot`, GitHub broker, and Cloudflare D1 adapter active; Hugging Face loaded/gated | Retain adapter gates and deny general plugin writes |
| GitHub | Live bounded read of both governed repositories; writes denied | Passed; retain repository-scoped read credential boundary |
| Brain | Nemotron Super active for the bounded operator session ending 2026-07-14T20:20:05Z | DEVELOPMENT only; renew or shut down explicitly |
| Candidate | `nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16` at `d51eab0d1f979ebc26b546e634a04f450d99158e` | Preserve repository and revision in response provenance |
| Bedrock route | Usability acceptance passed; 116 input / 7 output tokens; `$0.00002195`; per-request ceiling `$0.01` | Preserve evidence; no standing GPU or endpoint |
| Hugging Face endpoint | Disabled availability fallback; spend cap `$0` | Separate operator approval and hardware/spend acceptance |
| Dynamic storage | `cloudflare-d1`; durable restart/recovery proof passed | Retain token isolation and DEVELOPMENT-only schema |
| Task continuity | Tauri lists D1 tasks, restores turns, and sends a bounded prior-turn window | 12 turns / 24,000 characters by default |
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

## Capability pack

The checked-in `PROTOS-4` capability pack is the only capability inventory
installed into the guest. It pins one first-party skill and three plugin
contracts:

- `yeti-boot@1.0.0` is active through the deterministic local readback route;
- `github@0.1.8-2841cf9749ae` is active only through the METAXIS metadata
  broker, with writes denied;
- `hugging-face@1.0.0` is loaded but inactive pending its own endpoint and
  spend acceptance; and
- `cloudflare@0.1.2` is active only through the D1 storage adapter after Gate 3;
  general plugin writes remain denied.

The installer does not copy the host Codex plugin cache, browser sessions, app
connectors, MCP credentials, or macOS binaries into Ubuntu. Plugin metadata
does not execute third-party code. METAXIS adapters remain the execution
boundary, and `/api/v1/capabilities` reports the distinction between loaded
and active entries.

## Gate 2 — DEVELOPMENT inference

This gate is billable and must not start until the operator accepts the
per-token rate, region, model route, and spend ceiling.

This gate passed once on 2026-07-14. The route is currently off. The proof is
recorded in `docs/bedrock-development-validation-2026-07-14.md`.

1. Use Bedrock model `nvidia.nemotron-super-3-120b` in `us-east-1` for the
   primary DEVELOPMENT route. The observed rate is `$0.15` per million input
   tokens and `$0.65` per million output tokens.
2. Create a least-privilege assumable role limited to invocation of the named
   model. Never mount root or broad AWS credentials into METAXIS.
3. Export only temporary assumed-role credentials into an owner-only file
   outside the repository and mount it read-only.
4. Record the provider model ID, pinned source repository revision, license,
   region, runtime, and data-handling terms in the provider evidence.
5. Set `METAXIS_BRAIN_MODE=aws-bedrock`, the registered model/region metadata,
   and then set `METAXIS_EXTERNAL_MODEL_CALLS=1` last.
6. Run a synthetic/public prompt. Verify model repository, immutable revision,
   route, latency, token usage, and error evidence in the response.
7. Re-run a HIGH/NOFORN request and verify denial occurs before network I/O.

The independent comparison/availability candidate is versioned Bedrock model
`openai.gpt-oss-120b-1:0`. Switching is explicit and DEVELOPMENT-only. The
Hugging Face Super endpoint remains a cold, operator-approved fallback; it is
never an automatic HIGH/NOFORN fallback.

If any model coordinate, credential, custody flag, or route gate is absent,
METAXIS stays on the deterministic mock or denies the route.

## Gate 3 — Cloudflare D1 durability

1. Select the approved Cloudflare account and create the
   `metaxis-dynamic-state` D1 database.
2. Create a least-privilege D1 Edit token and store it in an owner-only
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

Gate 3 passed on 2026-07-14. The redacted proof is recorded in
`docs/cloudflare-d1-validation-2026-07-14.md`.

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
