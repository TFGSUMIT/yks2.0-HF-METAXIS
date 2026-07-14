# METAXIS Agent Instructions

METAXIS is the provider-neutral agentic harness. It owns reusable autonomy;
AXIS owns mission-specific authorization and guardrails.

## Operating Boundary

- The operator works from `PROD 0 YKS Ops Hub`. YKS Ops owns intent,
  authorization, requirements, roadmap state, governance, proof/readback, and
  links to implementation artifacts.
- This repository is the canonical home for all METAXIS source code, schemas,
  configurations, tests, evaluations, prototypes, architecture sources, design
  files, diagrams, UI assets, and rendered or exported design artifacts.
- Do not place or duplicate canonical METAXIS implementation or design
  artifacts in YKS Ops. Keep concise governance summaries and artifact links
  there; make implementation and design changes here.
- Root product authority remains YKS Ops issue 422. Phase 0 research authority
  remains issue 423. This repository's issue 1 remains a read-only mirror.

## Artifact Placement

- Keep executable implementation in `src/`, `scripts/`, `schemas/`, `configs/`,
  `evals/`, and `tests/` as appropriate.
- Keep canonical architecture and design sources in `docs/architecture/`.
- Keep reusable identity and visual assets in `assets/`.
- Keep generated or rendered design deliverables in `artifacts/design/` when
  that structure is needed.
- Record the authority issue or requirement, proof posture, provenance, and
  source-versus-rendered status for material artifacts.
- Before persistent edits, create or use an authority-linked `codex/*` branch.

## Boot Protocol

1. Read `README.md`, this file, and `docs/codex-project.md`.
2. Inspect `git status -sb`, the latest commit, and the configured remote.
3. Run `python3 -m unittest discover -s tests -v` with `PYTHONPATH=src:.` when
   the checked-in local environment has not already run the suite.
4. Read implementation issue #1 for the mirrored root posture and follow its
   YKS Ops authority link before changing scope.
5. Report the Phase 0 posture, active branch/worktree, validation state, and
   next authority-linked action.

## Rules

- Treat yks2.0-ops-hub issues 422 and 423 as the governing product sources.
- Treat this repository's issue 1 as a generated one-way mirror of issue 422;
  make root changes only in YKS Ops.
- Do not claim production activation from scaffolding or research artifacts.
- Keep model providers and runtimes behind the brain adapter contract.
- Pin model and runtime versions before evaluation claims.
- Record actual licenses and provenance; do not infer open-source status.
- Never place credentials, tokens, durable memory authority, or final action
  policy inside the model provider.
- Consequential actions must fail closed when authority is absent.
- Preserve evaluation, replay, recovery, and evidence hooks in every adapter.
- AXIS may declare mission overrides but must not fork the METAXIS core.

## Handoff

Report the active branch, changed artifacts, authority links, validation
result, proof posture, and any YKS Ops link/readback update needed to keep the
control plane current.

## Verification

Run:

    python3 -m unittest discover -s tests -v
    python3 -m metaxis status
    python3 scripts/environment_status.py
    .venv/bin/hf env
