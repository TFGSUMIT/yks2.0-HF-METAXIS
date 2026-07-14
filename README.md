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

## NemaShells installed application

NemaShells is the native METAXIS operator application. The laptop profile runs
the METAXIS service as a hardened workload on OrbStack's managed Docker engine,
uses Ubuntu as the isolated login/launcher shell, and keeps presentation state
only in the installed macOS app. The normal journey is:

```sh
orb start PROTOS-3
orb -m PROTOS-3
nemashells
```

One-time installation is documented in
[`docs/nemashells-install.md`](docs/nemashells-install.md). The same container
and systemd contract moves to the target Proxmox/KVM -> Debian VM -> Docker
stack without changing the app or brain adapter.

## HIGH/NOFORN hard gate

HIGH/NOFORN is a hard, fail-closed route requirement. The OrbStack laptop
profile accepts synthetic, public, or explicitly approved non-sensitive
development data only. External model calls are disabled. A route cannot be
eligible for HIGH/NOFORN until U.S.-origin model provenance, U.S.-person-only
administrative and workload access, approved U.S. placement, deny-by-default
egress, disabled external telemetry, credential custody, immutable pins, and
an authority record all pass. A public hosted API is not a fallback.

Nemotron 3 Nano 30B-A3B remains the primary evaluation candidate. Its quality
is not treated as proven until the repository-scale METAXIS evaluation passes.

## Phase 0: research and local application development

This repository starts with Hugging Face as the first discovery surface and
NVIDIA Nemotron as the first reference brain family. It does not select a
model by assumption.

The Phase 0 gate will:

- register immutable model repositories and revisions;
- record actual model, dataset, code, container, and service licenses;
- compare Nemotron with a provenance-approved U.S.-origin second candidate;
- normalize requests, responses, tool calls, errors, and provenance;
- measure quality, latency, tool use, recovery, cost, and data boundaries;
- prove export to an approved U.S.-person-controlled vLLM placement; and
- preserve a path to sovereign local inference.

## Repository layout

| Path | Purpose |
| --- | --- |
| src/metaxis | Provider-neutral harness contracts and CLI |
| apps/nemashells-macos | Native presentation-only NemaShells application |
| deployment | OrbStack, systemd, Docker, and Proxmox profiles |
| schemas/brain-contract | Machine-readable request and response envelopes |
| configs/providers | Research-only provider profiles |
| evals | Candidate register and repeatable evaluation design |
| docs/architecture | Ownership boundaries and migration architecture |
| docs/environment.md | Environment-variable and secret-handling contract |
| docs/huggingface-setup.md | Phase 0 Hugging Face toolchain and credential boundary |
| docs/cloudflare-d1-storage.md | Durable Cloudflare D1 dynamic-state contract and migration |
| scripts | Repository automation and redacted environment readback |
| tests | Contract and import checks |
| assets | METAXIS identity assets |

## Current posture

- Phase: 0 — research/discovery
- Provider profile: local deterministic mock; public hosted inference blocked for HIGH/NOFORN
- Reference model family: NVIDIA Nemotron, discovery-gated
- First open runtime: vLLM, conformance-gated
- Production inference: not activated
- Endpoint spending: not authorized
- HIGH/NOFORN processing: blocked in the laptop development profile
- Software license: selection pending an explicit governance decision

Public visibility does not itself grant a software license. License selection
is intentionally held as a decision gate so METAXIS does not invent legal
terms that its root issue has not authorized.

## Source truth

- Ops authority: https://github.com/LittleYeti-Dev/yks2.0-ops-hub
- METAXIS root: https://github.com/LittleYeti-Dev/yks2.0-ops-hub/issues/422
- Local root mirror: https://github.com/LittleYeti-Dev/yks2.0-HF-METAXIS/issues/1
- Research gate: https://github.com/LittleYeti-Dev/yks2.0-ops-hub/issues/423
- Hugging Face: https://huggingface.co/yks-metaxis

Issue 1 is a one-way mirror of YKS Ops issue 422. A scheduled workflow copies
the title, body, state, assignees, milestone, and exact label set every 15
minutes. Make root decisions in YKS Ops; direct edits to the mirror are
overwritten.
