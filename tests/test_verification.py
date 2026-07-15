import json
import unittest

from metaxis.verification import (
    ControlPlaneSnapshot,
    DraftParseError,
    parse_draft,
    render_blocked,
    render_verified,
    validate_draft,
)


def snapshot() -> ControlPlaneSnapshot:
    return ControlPlaneSnapshot(
        {
            "model.route": "aws-bedrock-super-development",
            "model.external_inference": True,
            "model.repository": "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16",
            "storage.backend": "cloudflare-d1",
            "storage.durable": True,
            "storage.application_writes": True,
            "github.mode": "metadata-read-only",
            "github.writes_allowed": False,
            "classification.high_noforn": "BLOCKED",
            "actions.consequential_allowed": False,
            "model.tools_available": False,
            "repository.branch_prefix": "codex/",
        }
    )


def raw_draft(**overrides) -> str:
    facts = snapshot().facts
    value = {
        "schema": "metaxis-draft/v1",
        "answer": "The route is active for DEVELOPMENT analysis.",
        "claims": [
            {"fact": key, "value": fact, "source": "metaxis-control-plane"}
            for key, fact in facts.items()
        ],
        "proposed_actions": [],
        "non_claims": ["No consequential action was executed."],
    }
    value.update(overrides)
    return json.dumps(value)


class VerificationTests(unittest.TestCase):
    def test_valid_registered_claims_render_verified(self) -> None:
        draft = parse_draft(raw_draft())
        result = validate_draft(draft, snapshot())
        self.assertTrue(result.valid)
        rendered = render_verified(draft, snapshot(), 1)
        self.assertTrue(rendered.startswith("VERIFIED"))
        self.assertIn("cloudflare-d1 · durable: true", rendered)
        self.assertIn("No write-capable action is registered", rendered)
        self.assertNotIn(draft.answer, rendered)

    def test_claim_mismatch_is_rejected(self) -> None:
        value = json.loads(raw_draft())
        value["claims"][1]["value"] = False
        result = validate_draft(parse_draft(json.dumps(value)), snapshot())
        self.assertFalse(result.valid)
        self.assertIn("claim_mismatch", {issue.code for issue in result.issues})

    def test_missing_claim_is_filled_but_unknown_claim_is_rejected(self) -> None:
        value = json.loads(raw_draft())
        value["claims"].pop()
        value["claims"].append(
            {"fact": "invented.fact", "value": True, "source": "metaxis-control-plane"}
        )
        result = validate_draft(parse_draft(json.dumps(value)), snapshot())
        codes = {issue.code for issue in result.issues}
        self.assertNotIn("missing_claim", codes)
        self.assertIn("unknown_claim", codes)

        value["claims"].pop()
        self.assertTrue(validate_draft(parse_draft(json.dumps(value)), snapshot()).valid)

    def test_unapproved_schema_action_is_rejected(self) -> None:
        value = json.loads(raw_draft())
        value["proposed_actions"] = [{
            "kind": "d1_schema_change",
            "description": "Create yeti_sightings_log.",
        }]
        result = validate_draft(parse_draft(json.dumps(value)), snapshot())
        codes = {issue.code for issue in result.issues}
        self.assertIn("action_not_registered", codes)
        self.assertIn("action_authority_absent", codes)

    def test_known_prose_contradictions_are_rejected(self) -> None:
        value = json.loads(raw_draft())
        value["answer"] = (
            "No external inference occurred. D1 did not persist state. "
            "Use feat/yeti and CREATE TABLE yeti_sightings_log."
        )
        result = validate_draft(parse_draft(json.dumps(value)), snapshot())
        codes = {issue.code for issue in result.issues}
        self.assertIn("prose_external_inference_conflict", codes)
        self.assertIn("prose_persistence_conflict", codes)
        self.assertIn("prose_branch_prefix_conflict", codes)

    def test_live_d1_memory_wording_is_rejected(self) -> None:
        draft = json.loads(raw_draft())
        draft["answer"] = "Storage is non-durable memory-based storage."

        result = validate_draft(parse_draft(json.dumps(draft)), snapshot())

        codes = {issue.code for issue in result.issues}
        self.assertIn("prose_durability_conflict", codes)
        self.assertIn("prose_storage_backend_conflict", codes)

    def test_action_descriptions_cannot_smuggle_write_operations(self) -> None:
        draft = json.loads(raw_draft())
        draft["proposed_actions"] = [
            {
                "kind": "analysis",
                "description": "Create table yeti_sightings_log and git push it.",
            }
        ]

        result = validate_draft(parse_draft(json.dumps(draft)), snapshot())

        self.assertIn("unstructured_action", {issue.code for issue in result.issues})

    def test_malformed_provider_output_fails_closed(self) -> None:
        with self.assertRaises(DraftParseError):
            parse_draft("not json")
        blocked = render_blocked(snapshot(), 2, ())
        self.assertTrue(blocked.startswith("BLOCKED"))


if __name__ == "__main__":
    unittest.main()
