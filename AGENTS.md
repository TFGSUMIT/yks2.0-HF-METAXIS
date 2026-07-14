# METAXIS Agent Instructions

METAXIS is the provider-neutral agentic harness. It owns reusable autonomy;
AXIS owns mission-specific authorization and guardrails.

## Rules

- Treat yks2.0-ops-hub issues 422 and 423 as the governing product sources.
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

