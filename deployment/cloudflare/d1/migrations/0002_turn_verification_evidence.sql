-- Authority: YKS Ops #441 -> #456 -> #471; execution boundary #433 -> #448 -> #463
-- DEVELOPMENT-only self-correction evidence. No credential or action authority is stored.

ALTER TABLE metaxis_turns
    ADD COLUMN verification_json TEXT NOT NULL DEFAULT '{}';

ALTER TABLE metaxis_turns
    ADD COLUMN brain_evidence_json TEXT NOT NULL DEFAULT '{}';
