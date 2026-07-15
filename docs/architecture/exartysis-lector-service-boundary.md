# EXARTYSIS / LECTOR Service Boundary

Status: Phase 0 development contract  
Authority: YKS Ops #422, EXARTYSIS #484, LECTOR #483

## Placement

EXARTYSIS remains the NemaShells-facing execution harness inside the hardened
METAXIS container. LECTOR is a separate CPU-first container on the private
`metaxis_private` Docker network. It has no host-published port.

```text
NemaShells -> EXARTYSIS / METAXIS -> LECTOR
                                    -> source registry / index / corpus

TESTIMONIUM / D1 <- receipts and metadata only
```

NemaShells must not call LECTOR directly. LECTOR must not execute tools. AXIS
must supply a source-eligibility decision before retrieval. D1 remains proof
and metadata storage; it is not the LECTOR corpus or vector store.

## Phase 0 Slice

This repository provides a private `/healthz` endpoint and an EXARTYSIS-only
`POST /api/v1/context` contract. The first adapter is deterministic,
in-memory, lexical matching for public/synthetic fixtures. It is not a vector
database, embedding service, selected backend, or operational RAG pipeline.

Every delivered item includes source ID, version, content hash, chunk ID,
citation, freshness, and score. Missing eligibility, unavailable eligible
sources, no match, and exhausted context budgets are explicit outcomes.

## Deployment Boundary

`compose.yaml` defines the separate service for local development, but the
OrbStack installer does not start it yet. That remains an explicit later
activation gate with a registry/corpus fixture, service authentication,
AXIS authorization, evaluation/replay evidence, and operator approval.

Omen's RTX 2060 8 GB is only a future DEVELOPMENT embedding/cuVS comparison
backend. Shamus-2 is the gated POC host; Shamus-1 is the portability contrast.

## Non-Claims

- No LECTOR container is deployed by this change.
- No corpus, index, vector backend, embedding model, or GPU route is selected.
- No source is eligible without an explicit authority allowlist.
- No protected data, HIGH/NOFORN processing, direct operator route, or tool
  execution is authorized.
