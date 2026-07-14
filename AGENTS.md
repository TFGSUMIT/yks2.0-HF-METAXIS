# METAXIS Agent Instructions

METAXIS is the provider-neutral agentic harness. It owns reusable autonomy;
AXIS owns mission-specific authorization and guardrails.

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

## Verification

Run:

    python3 -m unittest discover -s tests -v
    python3 -m metaxis status
