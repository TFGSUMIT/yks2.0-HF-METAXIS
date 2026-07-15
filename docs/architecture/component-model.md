# METAXIS Component Model

Authority: YKS Ops root #422  
Capability roots: #484 EXARTYSIS; #483 LECTOR  
Derivative bridge roots: #485 EXARTYSIS; #486 LECTOR  
Architecture review: #487 NVIDIA OpenShell / NemaShells boundary  
Proof posture: manual-placeholder; component decision stamped, implementation
evidence remains requirement-specific

## Canonical hierarchy

```text
METAXIS
├── EXARTYSIS — sovereign execution harness
├── LECTOR — retrieval-augmented generation component / METAXIS RAG
└── NemaShells — operator interface
```

EXARTYSIS, LECTOR, and NemaShells are first-class sibling components directly
under METAXIS. None owns or contains another. They exchange state, context,
commands, health, and evidence only through versioned METAXIS contracts.

## Ownership

| Component | Owns | Does not own |
| --- | --- | --- |
| EXARTYSIS | Persistent execution state; workspace isolation and handoff; agent/tool/capability mediation; bounded delegation; model/runtime routing; local enforcement; lifecycle, recovery, and evidence hooks. | RAG, operator presentation, mission authority, evidence certification. |
| LECTOR | The METAXIS RAG: governed source registry, fetch, normalization, retrieval, ranking, curation, citations, context budgets, retrieval evaluation, and source-to-context evidence. | Execution-harness state, operator presentation, mission authority, durable source truth. |
| NemaShells | Installed operator-interface contract, steering, health, provenance, gap, denial, conflict, citation, and proof-posture display. | Execution, RAG, mission authority, source truth, evidence certification. |

## Derivative continuity

Capability roots remain under the METAXIS epic. Bridge roots map downstream
derivatives without copying or transferring the root requirements:

- AXIS adds mission authority, operational guardrails, trusted/degraded-mode
  behavior, and proof-bound action.
- FABRICA consumes governed orchestration contracts.
- SYMBOLON supplies actor and delegation identity semantics.
- CUSTODIA supplies credential and trust-material custody.
- TENAX consumes adversarial, policy, retrieval, and safety evaluation hooks.
- TESTIMONIUM witnesses runtime and retrieval events.
- ACTA packages accepted evidence and provenance.
- OCULUS consumes evidence-backed operator readback.
- ARBITER/NIMBUS may supply provider and placement routing.

No derivative product becomes a METAXIS co-owner or may fork the common core.

## EXARTYSIS Accelerated Execution Plane

The Accelerated Execution Plane is internal to EXARTYSIS and is not a fourth
METAXIS component. Its provider-neutral contract covers isolated workspaces and
processes, filesystem/network/process/credential/inference policy, lifecycle,
interruption, rollback, denial, telemetry, and evidence.

```text
EXARTYSIS
└── Accelerated Execution Plane
    ├── native provider — required and sufficient
    └── external-provider extension point — dormant / no current selection
```

METAXIS must boot, operate, recover, test, and exit with only its native
provider. No current requirement selects NVIDIA OpenShell or another external
provider. The dormant extension point may be activated only by a future
requirement and separate qualification. Provider identity never confers
authority, custody, evidence status, or product identity. Authority issue #488 and
`YKS-REQ-MTX-EXARTYSIS-011` own this plane.

## External NVIDIA candidates

- NVIDIA OpenShell is cataloged/deferred with no current METAXIS requirement.
  It is not NemaShells, not a METAXIS component, and not an admitted provider
  or dependency. Issue #487 records the completed aClive review. A future
  requirement and separate operator ruling would be required before intake or
  qualification.

## Deployment allocation

| Phase | EXARTYSIS | LECTOR |
| --- | --- | --- |
| Development | Existing hardened `metaxis` container on OrbStack; PROTOS-3 is the login/launcher path. | Separate CPU-first container on the same private network with separate corpus/index/state boundaries. |
| GPU experiment | Remains on the OrbStack METAXIS profile. | Omen RTX 2060 SUPER 8GB may host a DEVELOPMENT comparison backend only; Omen remains a lab bridge. |
| POC | Separate service on Shamus-2. | Separate service on Shamus-2, close to the authorized corpus and AXIS eligibility gate; split an approved GPU backend only when measured need exists. |
| Portability | Reproduce on Shamus-1 as the OCI/provider contrast. | Reproduce the same contract on Shamus-1 with exportable corpus/index manifest and no backend lock-in. |

NemaShells calls EXARTYSIS. EXARTYSIS requests context from LECTOR. NemaShells
does not call LECTOR directly; LECTOR does not execute tools; D1 remains
proof/metadata storage rather than a vector or corpus backend.
- NVIDIA RAG Blueprint, Streaming RAG, and cuVS are candidate LECTOR backends.
  They do not become a second METAXIS RAG or source-truth authority.
- Every NVIDIA path remains external, third-party-license intake for public,
  synthetic, or explicitly approved non-sensitive evaluation. HIGH/NOFORN use
  remains blocked until separately approved custody, location, egress,
  telemetry, provenance, support, and authority gates pass.

## Requirement roots

- `YKS-REQ-MTX-EXARTYSIS-001` through `-011` name the sovereign execution
  harness denominator.
- `YKS-REQ-MTX-LECTOR-001` through `-010` name the METAXIS RAG denominator.
- Existing `YKS-REQ-MTX-UI-*` and delivery chain #474 → #475 → #476 carry the
  NemaShells interface denominator.

The requirement and issue roots prove architecture and planned obligations.
They do not prove component completion, production readiness, or protected-data
eligibility.
