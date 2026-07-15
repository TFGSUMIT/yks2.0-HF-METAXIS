"""Deterministic validation and repair contracts for model-authored drafts."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Mapping, Sequence


SCHEMA_ID = "metaxis-draft/v1"
FACT_SOURCE = "metaxis-control-plane"
MAX_DRAFT_BYTES = 100_000
READ_ONLY_ACTIONS = {"none", "analysis", "read_only_probe"}
WRITE_ACTIONS = {
    "repository_write",
    "github_write",
    "d1_schema_change",
    "tool_execution",
    "consequential_action",
}
ACTION_KINDS = READ_ONLY_ACTIONS | WRITE_ACTIONS


@dataclass(frozen=True, slots=True)
class ControlPlaneSnapshot:
    facts: Mapping[str, Any]
    approved_action_ids: tuple[str, ...] = ()

    @property
    def snapshot_id(self) -> str:
        payload = json.dumps(
            {
                "facts": dict(self.facts),
                "approved_action_ids": list(self.approved_action_ids),
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()[:16]

    def to_prompt_value(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "facts": dict(self.facts),
            "approved_action_ids": list(self.approved_action_ids),
        }


@dataclass(frozen=True, slots=True)
class FactClaim:
    fact: str
    value: Any
    source: str


@dataclass(frozen=True, slots=True)
class ProposedAction:
    kind: str
    description: str
    action_id: str | None = None
    authority_record: str | None = None


@dataclass(frozen=True, slots=True)
class DraftEnvelope:
    answer: str
    claims: tuple[FactClaim, ...]
    proposed_actions: tuple[ProposedAction, ...]
    non_claims: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "detail": self.detail}


@dataclass(frozen=True, slots=True)
class ValidationResult:
    valid: bool
    issues: tuple[ValidationIssue, ...]


class DraftParseError(ValueError):
    """Raised when a provider response is not the registered draft schema."""


def output_contract(snapshot: ControlPlaneSnapshot) -> str:
    """Return the provider-neutral JSON-only output contract."""

    return "\n".join(
        [
            "Return ONLY one JSON object. Do not use markdown fences.",
            f'Use schema \"{SCHEMA_ID}\" with exactly these top-level fields:',
            '- "schema": the schema ID;',
            '- "answer": operator-facing analysis, with recommendations excluded;',
            '- "claims": zero or one object for any snapshot fact referenced by the draft, each with "fact", "value", and source "metaxis-control-plane"; omitted facts are supplied deterministically by METAXIS;',
            '- "proposed_actions": zero or more objects with "kind", "description", optional "action_id", and optional "authority_record";',
            '- "non_claims": zero or more short strings.',
            "Put every recommendation or requested operation in proposed_actions, never in answer.",
            "Write-capable actions require an action_id present in approved_action_ids and an authority_record.",
            "Do not invent a schema, branch, issue, action ID, authority record, completion state, or runtime fact.",
            "METAXIS_CONTROL_PLANE_SNAPSHOT_JSON="
            + json.dumps(snapshot.to_prompt_value(), separators=(",", ":"), sort_keys=True),
        ]
    )


def _strip_fence(raw: str) -> str:
    value = raw.strip()
    match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", value, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else value


def parse_draft(raw: str) -> DraftEnvelope:
    if len(raw.encode("utf-8")) > MAX_DRAFT_BYTES:
        raise DraftParseError("draft exceeds the registered size ceiling")
    try:
        value = json.loads(_strip_fence(raw))
    except json.JSONDecodeError as error:
        raise DraftParseError("provider response is not valid JSON") from error
    if not isinstance(value, dict):
        raise DraftParseError("provider response must be a JSON object")
    if value.get("schema") != SCHEMA_ID:
        raise DraftParseError("provider response has an unregistered schema")
    expected = {"schema", "answer", "claims", "proposed_actions", "non_claims"}
    if set(value) != expected:
        raise DraftParseError("provider response has missing or unknown top-level fields")

    answer = value.get("answer")
    if not isinstance(answer, str) or not answer.strip():
        raise DraftParseError("answer must be a non-empty string")

    raw_claims = value.get("claims")
    if not isinstance(raw_claims, list) or len(raw_claims) > 64:
        raise DraftParseError("claims must be a bounded array")
    claims: list[FactClaim] = []
    for item in raw_claims:
        if not isinstance(item, dict) or set(item) != {"fact", "value", "source"}:
            raise DraftParseError("claim does not match the registered schema")
        if not isinstance(item["fact"], str) or not isinstance(item["source"], str):
            raise DraftParseError("claim fact and source must be strings")
        claims.append(FactClaim(item["fact"], item["value"], item["source"]))

    raw_actions = value.get("proposed_actions")
    if not isinstance(raw_actions, list) or len(raw_actions) > 16:
        raise DraftParseError("proposed_actions must be a bounded array")
    actions: list[ProposedAction] = []
    for item in raw_actions:
        if not isinstance(item, dict):
            raise DraftParseError("proposed action must be an object")
        if not set(item).issubset({"kind", "description", "action_id", "authority_record"}):
            raise DraftParseError("proposed action has unknown fields")
        kind = item.get("kind")
        description = item.get("description")
        if kind not in ACTION_KINDS or not isinstance(description, str) or not description.strip():
            raise DraftParseError("proposed action kind or description is invalid")
        action_id = item.get("action_id")
        authority_record = item.get("authority_record")
        if action_id is not None and not isinstance(action_id, str):
            raise DraftParseError("action_id must be a string or null")
        if authority_record is not None and not isinstance(authority_record, str):
            raise DraftParseError("authority_record must be a string or null")
        actions.append(ProposedAction(kind, description, action_id, authority_record))

    raw_non_claims = value.get("non_claims")
    if (
        not isinstance(raw_non_claims, list)
        or len(raw_non_claims) > 32
        or not all(isinstance(item, str) and item.strip() for item in raw_non_claims)
    ):
        raise DraftParseError("non_claims must be a bounded string array")
    return DraftEnvelope(
        answer=answer.strip(),
        claims=tuple(claims),
        proposed_actions=tuple(actions),
        non_claims=tuple(item.strip() for item in raw_non_claims),
    )


def _prose_issues(answer: str, snapshot: ControlPlaneSnapshot) -> list[ValidationIssue]:
    facts = snapshot.facts
    rules: list[tuple[bool, str, str, str]] = [
        (
            facts.get("model.external_inference") is True,
            r"\b(?:no external (?:model calls?|inference)|external inference\s*(?::|is)?\s*false|external api\s*(?::|is)?\s*denied)\b",
            "prose_external_inference_conflict",
            "answer contradicts the active external inference route",
        ),
        (
            facts.get("storage.durable") is True,
            r"\b(?:(?:storage|d1|writes?)\s+(?:are\s+|is\s+)?(?:not|non[- ]?)durable|durable\s*(?::|is)?\s*false|non[- ]durable\s+(?:storage|memory))\b",
            "prose_durability_conflict",
            "answer contradicts durable storage readback",
        ),
        (
            facts.get("storage.backend") == "cloudflare-d1",
            r"\b(?:(?:storage\s+is\s+)?(?:memory[- ]based|memory-development|in-memory)(?:\s+storage)?|confined to memory)\b",
            "prose_storage_backend_conflict",
            "answer contradicts the Cloudflare D1 storage backend",
        ),
        (
            facts.get("storage.application_writes") is True,
            r"\b(?:(?:d1|nemashells|surface)\s+(?:cannot|can not|does not|did not)\s+(?:persist|append|write)|no state (?:was )?persisted)\b",
            "prose_persistence_conflict",
            "answer contradicts DEVELOPMENT thread persistence",
        ),
        (
            "Super" in str(facts.get("model.repository", "")),
            r"\bNemotron[^\n.]*Nano\b",
            "prose_model_conflict",
            "answer names Nano while the registered route uses Super",
        ),
        (
            facts.get("github.writes_allowed") is False,
            r"\bgithub writes?\s+(?:are\s+)?(?:enabled|allowed|authorized)\b",
            "prose_github_authority_conflict",
            "answer contradicts the GitHub write boundary",
        ),
        (
            facts.get("actions.consequential_allowed") is False,
            r"\bconsequential actions?\s+(?:are\s+)?(?:enabled|allowed|authorized)\b",
            "prose_action_authority_conflict",
            "answer contradicts the consequential-action boundary",
        ),
        (
            facts.get("repository.branch_prefix") == "codex/",
            r"\b(?:dev|feat)/[A-Za-z0-9._/-]+",
            "prose_branch_prefix_conflict",
            "answer names an unregistered repository branch prefix",
        ),
    ]
    issues = [
        ValidationIssue(code, detail)
        for enabled, pattern, code, detail in rules
        if enabled and re.search(pattern, answer, re.IGNORECASE)
    ]
    if re.search(
        r"\b(?:CREATE\s+TABLE|apply (?:a )?migration|git push|commit and push|open (?:a )?(?:PR|pull request)|update (?:the )?(?:issue|schema))\b",
        answer,
        re.IGNORECASE,
    ):
        issues.append(
            ValidationIssue(
                "unstructured_action",
                "answer contains an operation that must be represented in proposed_actions",
            )
        )
    return issues


def validate_draft(
    draft: DraftEnvelope, snapshot: ControlPlaneSnapshot
) -> ValidationResult:
    issues: list[ValidationIssue] = []
    claims_by_fact: dict[str, FactClaim] = {}
    for claim in draft.claims:
        if claim.fact in claims_by_fact:
            issues.append(ValidationIssue("duplicate_claim", f"duplicate claim: {claim.fact}"))
            continue
        claims_by_fact[claim.fact] = claim
        if claim.fact not in snapshot.facts:
            issues.append(ValidationIssue("unknown_claim", f"unknown fact: {claim.fact}"))
        elif claim.value != snapshot.facts[claim.fact]:
            issues.append(ValidationIssue("claim_mismatch", f"claim conflicts with snapshot: {claim.fact}"))
        if claim.source != FACT_SOURCE:
            issues.append(ValidationIssue("invalid_claim_source", f"unregistered source for: {claim.fact}"))

    for action in draft.proposed_actions:
        if action.kind in WRITE_ACTIONS:
            if not action.action_id or action.action_id not in snapshot.approved_action_ids:
                issues.append(
                    ValidationIssue(
                        "action_not_registered",
                        f"write-capable action is not in the approved action catalog: {action.kind}",
                    )
                )
            if not action.authority_record:
                issues.append(
                    ValidationIssue(
                        "action_authority_absent",
                        f"write-capable action lacks an authority record: {action.kind}",
                    )
                )
    issues.extend(_prose_issues(draft.answer, snapshot))
    for index, action in enumerate(draft.proposed_actions):
        for issue in _prose_issues(action.description, snapshot):
            issues.append(
                ValidationIssue(
                    issue.code,
                    f"proposed_actions[{index}] {issue.detail}",
                )
            )
    return ValidationResult(valid=not issues, issues=tuple(issues))


def repair_instruction(
    snapshot: ControlPlaneSnapshot, issues: Sequence[ValidationIssue]
) -> str:
    return "\n".join(
        [
            "METAXIS rejected the previous draft. Return a complete replacement JSON object.",
            "Do not defend or explain the rejected draft.",
            "VALIDATION_ISSUES_JSON="
            + json.dumps([issue.to_dict() for issue in issues], separators=(",", ":")),
            output_contract(snapshot),
        ]
    )


def render_verified(
    draft: DraftEnvelope,
    snapshot: ControlPlaneSnapshot,
    attempts: int,
) -> str:
    facts = snapshot.facts
    lines = [
        "VERIFIED · registered METAXIS facts only",
        f"Snapshot: {snapshot.snapshot_id} · attempts: {attempts}",
        "",
        "Registered control-plane state",
        f"- Active route: {facts['model.route']}",
        f"- External inference for this turn: {'yes' if facts['model.external_inference'] else 'no'}",
        f"- Model repository: {facts['model.repository']}",
        f"- Storage: {facts['storage.backend']} · durable: {str(facts['storage.durable']).lower()}",
        f"- DEVELOPMENT turn persistence: {'enabled' if facts['storage.application_writes'] else 'disabled'}",
        f"- GitHub: {facts['github.mode']} · writes: {'allowed' if facts['github.writes_allowed'] else 'denied'}",
        f"- HIGH/NOFORN: {facts['classification.high_noforn']}",
        f"- Consequential actions: {'allowed' if facts['actions.consequential_allowed'] else 'blocked'}",
        f"- Model tools: {'available' if facts['model.tools_available'] else 'unavailable'}",
        f"- Repository branch prefix: {facts['repository.branch_prefix']}",
        "",
        "Action gate",
    ]
    if not snapshot.approved_action_ids:
        lines.append("- No write-capable action is registered or authorized.")
    elif not draft.proposed_actions:
        lines.append("- No action proposed by the model.")
    else:
        for action in draft.proposed_actions:
            posture = "READ-ONLY" if action.kind in READ_ONLY_ACTIONS else "AUTHORIZED-PROPOSAL"
            lines.append(f"- {posture} · {action.kind}")
    lines.extend(
        [
            "",
            "Model synthesis",
            "- Withheld from operational guidance; this verifier proves registered facts and action authority, not arbitrary prose semantics.",
        ]
    )
    return "\n".join(lines)


def render_blocked(
    snapshot: ControlPlaneSnapshot,
    attempts: int,
    issues: Sequence[ValidationIssue],
) -> str:
    lines = [
        "BLOCKED · METAXIS verification failed closed",
        f"Snapshot: {snapshot.snapshot_id} · attempts: {attempts}",
        "",
        "The model draft was not shown as operational guidance because it could not be reconciled with registered control-plane truth.",
        "Validation issues",
    ]
    lines.extend(f"- {issue.code}: {issue.detail}" for issue in issues)
    lines.extend(
        [
            "",
            "No proposed action was authorized or executed.",
        ]
    )
    return "\n".join(lines)
