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

`PROTOS-4` was stopped and retired by operator ruling on 2026-07-15. Its
OrbStack disk, checked-in prototype, and validation notes are retained as
historical evidence only; the machine is not a forward NemaShells delivery or
acceptance dependency. NemaShells remains the internal interface/package
contract until separately migrated, with no Tauri implementation or fallback
required. Promoted presentation follows the SkipJack Console Design Language
and does not use NemaShells as visible branding.

## SkipJack Console Design Language

Every METAXIS UI uses `SKIPJACK-CONSOLE-DL-1.0` and cites
`MTX-ART-DL-20260715-004` as its source design artifact. The canonical
specification and Standard Clean / Complex Unpacked references live under
`assets/brand/`. METAXIS is the visible product identity; SkipJack is the
parent brand and supplies the `Powered by SkipJack` endorsement.

The design stamp is operator-accepted and has row-backed D1 receipt
`MTX-DESIGN-OUTPUT-SJCDL-20260715-001`. It does not claim that the current
application fully implements the design language, that the package is
production-ready, or that HIGH/NOFORN processing is authorized.

## HIGH/NOFORN hard gate

HIGH/NOFORN is a hard, fail-closed route requirement. The OrbStack laptop
profile accepts synthetic, public, or explicitly approved non-sensitive
development data only. External calls may be enabled only through a registered,
cost-bounded DEVELOPMENT route. A route cannot be
eligible for HIGH/NOFORN until U.S.-origin model provenance, U.S.-person-only
administrative and workload access, approved U.S. placement, deny-by-default
egress, disabled external telemetry, credential custody, immutable pins, and
an authority record all pass. A public hosted API is not a fallback.

Nemotron 3 Super 120B-A12B remains the primary evaluation candidate. Its quality
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
| apps/nemashells-tauri | Historical Tauri 2 prototype retained as superseded evidence; not a forward delivery requirement |
| deployment | OrbStack, systemd, Docker, and Proxmox profiles |
| src/metaxis/capabilities | Pinned skill and plugin inventory for PROTOS-4 |
| schemas/brain-contract | Machine-readable request and response envelopes |
| configs/providers | Research-only provider profiles |
| evals | Candidate register and repeatable evaluation design |
| docs/architecture | Ownership boundaries and migration architecture |
| docs/architecture/self-correction-harness.md | Structured repair, deterministic readback, and fail-closed action verification |
| docs/environment.md | Environment-variable and secret-handling contract |
| docs/huggingface-setup.md | Phase 0 Hugging Face toolchain and credential boundary |
| docs/aws-bedrock-development.md | Bedrock Super route, availability fallback, and credential boundary |
| docs/github-read-broker.md | Fail-closed GitHub metadata boundary for NemaShells |
| docs/cloudflare-d1-storage.md | Durable Cloudflare D1 dynamic-state contract and migration |
| docs/cloudflare-d1-validation-2026-07-14.md | Redacted D1 migration, isolation, and restart/recovery proof |
| docs/functional-prototype-activation.md | No-spend-to-live activation gates and acceptance proof |
| docs/protos-4-usability-validation-2026-07-14.md | Durable task, bounded context, live model, and negative proof |
| docs/self-correction-validation-2026-07-14.md | Live positive, adversarial, persistence, and route-denial proof |
| scripts | Repository automation and redacted environment readback |
| tests | Contract and import checks |
| assets | METAXIS identity assets |
| assets/brand | Versioned METAXIS lockup, SkipJack Console Design Language, reference views, and artifact metadata |

## Current posture

- Phase: 0 — research/discovery
- Provider profile: time-bounded AWS Bedrock DEVELOPMENT route with deterministic mock fallback; all public hosted inference blocked for HIGH/NOFORN
- Reference model family: NVIDIA Nemotron, discovery-gated
- First open runtime: vLLM, conformance-gated
- Production inference: not activated
- Endpoint spending: Bedrock on-demand DEVELOPMENT calls authorized within the registered per-request ceiling; no standing endpoint
- HIGH/NOFORN processing: blocked in the laptop development profile
- Functional prototype: DEVELOPMENT gates passed for the installed shell, GitHub live read, verified/blocked inference paths, and D1 evidence durability
- PROTOS-4: retired and stopped on 2026-07-15; disk and historical proof retained, with no forward delivery dependency
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
