# METAXIS

![METAXIS sasquatch avatar](assets/metaxis-sasquatch-avatar.png)

YKS Ops PROD 0.1 METAXIS is the provider-neutral agentic box at the beginning
of the YKS core-product critical path.

> North Star: own the autonomy; progressively reclaim the brain.

METAXIS owns threads, plans, agent lifecycle, workspaces, tools, governed
memory, permissions, recovery, evaluation, replay, and evidence hooks. AXIS is
the mission-focused derivative that consumes a pinned METAXIS capability set
and adds mission authority, guardrails, degraded-mode rules, and proof-bound
execution.

## Architecture map

🟩 YKS Ops → 🟦 METAXIS → 🟥 AXIS → 🟪 mission execution →
🟩 TESTIMONIUM / ACTA proof → 🟪 OCULUS readback

## Phase 0: Hugging Face research and discovery

This repository starts with Hugging Face as the first discovery surface and
NVIDIA Nemotron as the first reference brain family. It does not select a
model by assumption.

The Phase 0 gate will:

- register immutable model repositories and revisions;
- record actual model, dataset, code, container, and service licenses;
- compare Nemotron with credible non-NVIDIA candidates;
- normalize requests, responses, tool calls, errors, and provenance;
- measure quality, latency, tool use, recovery, cost, and data boundaries;
- prove export from hosted inference to rented vLLM; and
- preserve a path to sovereign local inference.

## Repository layout

| Path | Purpose |
| --- | --- |
| src/metaxis | Provider-neutral harness contracts and CLI |
| schemas/brain-contract | Machine-readable request and response envelopes |
| configs/providers | Research-only provider profiles |
| evals | Candidate register and repeatable evaluation design |
| docs/architecture | Ownership boundaries and migration architecture |
| tests | Contract and import checks |
| assets | METAXIS identity assets |

## Current posture

- Phase: 0 — research/discovery
- Provider profile: Hugging Face first
- Reference model family: NVIDIA Nemotron, discovery-gated
- First open runtime: vLLM, conformance-gated
- Production inference: not activated
- Endpoint spending: not authorized
- Software license: selection pending an explicit governance decision

Public visibility does not itself grant a software license. License selection
is intentionally held as a decision gate so METAXIS does not invent legal
terms that its root issue has not authorized.

## Source truth

- Ops authority: https://github.com/LittleYeti-Dev/yks2.0-ops-hub
- METAXIS root: https://github.com/LittleYeti-Dev/yks2.0-ops-hub/issues/422
- Research gate: https://github.com/LittleYeti-Dev/yks2.0-ops-hub/issues/423
- Hugging Face: https://huggingface.co/yks-metaxis
