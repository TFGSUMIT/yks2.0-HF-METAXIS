# METAXIS self-correction harness

Status: Phase 0 DEVELOPMENT control-plane verifier

Authority: YKS Ops #422 → #428 → #441 → #456 → #471, with execution-boundary cross-proof #433 → #448 → #463

## Outcome

METAXIS no longer presents a provider response directly as operational truth.
For every external DEVELOPMENT turn, the server creates a non-secret snapshot
of registered control-plane facts, requests a structured draft, validates the
draft, performs at most one repair, and either renders registered facts
deterministically or fails closed.

The model remains a draft generator. METAXIS remains the authority boundary.

## Verification loop

1. Read the current route, immutable model coordinate, storage posture,
   GitHub posture, classification gate, action posture, tool posture, and
   repository branch prefix from the live control plane.
2. Hash those values into a snapshot ID and supply the snapshot through the
   provider-neutral `metaxis-draft/v1` contract.
3. Parse a bounded JSON object. Unknown fields, schemas, claim sources, action
   kinds, and oversized arrays fail validation.
4. Require every model-cited control-plane claim to match the snapshot.
   Omitted facts are filled by METAXIS, not by another model call.
5. Reject write-capable proposals unless their action ID is present in the
   approved action catalog and an authority record is supplied. The Phase 0
   catalog is empty.
6. Reject known contradictory prose and operations hidden in either the answer
   or an action description.
7. On failure, issue one complete replacement request. The registered NVIDIA
   Bedrock route receives the control-plane directive in the first user turn
   because its Converse system field is accepted but was not followed reliably
   in live testing.
8. After two failed drafts, persist and return a `BLOCKED` turn. No provider
   text is displayed as guidance and no action is authorized.
9. On success, render the full fact packet from the snapshot. Free-form model
   synthesis is withheld because structural validation does not prove arbitrary
   prose semantics.

## Evidence and recovery

Every persisted external turn contains:

- verification status, mode, attempts, snapshot ID, and terminal issues;
- provider, model repository, immutable revision, runtime, and runtime version;
- aggregate input tokens, output tokens, latency, and calculated cost across
  the draft and repair calls; and
- the deterministic operator-facing result.

Cloudflare D1 migration `0002_turn_verification_evidence.sql` adds the
verification and brain-evidence columns. A container restart must recover both
objects with the turn.

## Fail-closed boundaries

- Blank or misnamed turn payloads return HTTP 400 and never reach a provider.
- HIGH/NOFORN returns HTTP 403 before inference.
- Provider failures return a bounded error and are not persisted as answers.
- Unregistered write proposals fail validation; the model has no tools or
  credentials.
- GitHub remains metadata read-only.
- The D1, GitHub, and AWS credential files are mounted read-only and are never
  included in the snapshot or model request.

## Explicit limits

This is not a general semantic truth engine. It proves only the registered
control-plane facts and action authority represented in the snapshot. Model
synthesis stays withheld until a separately evaluated semantic verifier can
demonstrate acceptable false-accept and false-reject rates. The harness does
not establish model sufficiency, production activation, HIGH/NOFORN
eligibility, or consequential-action authority.
