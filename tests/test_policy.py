import unittest
from dataclasses import replace

from metaxis.policy import (
    Classification,
    DEVELOPMENT_ROUTE,
    RouteProfile,
    evaluate_route,
)


class RoutePolicyTests(unittest.TestCase):
    def test_development_route_denies_high_noforn(self) -> None:
        decision = evaluate_route(DEVELOPMENT_ROUTE, Classification.HIGH_NOFORN)
        self.assertFalse(decision.eligible)
        self.assertEqual(decision.status, "BLOCKED")
        self.assertIn("YKS-REQ-MTX-026", decision.requirement_ids)

    def test_public_development_data_can_use_mock_route(self) -> None:
        decision = evaluate_route(DEVELOPMENT_ROUTE, Classification.DEVELOPMENT)
        self.assertTrue(decision.eligible)
        self.assertEqual(decision.status, "ELIGIBLE-DEVELOPMENT-ONLY")

    def test_complete_us_control_profile_can_be_eligible(self) -> None:
        profile = RouteProfile(
            route_id="proof-only",
            provider="self-hosted",
            model_repository="approved/model",
            model_revision="sha256:proof",
            model_developer_country="US",
            runtime="vllm",
            placement="approved-us-boundary",
            us_person_admin_only=True,
            us_person_user_only=True,
            us_location_only=True,
            egress_default_deny=True,
            external_telemetry_disabled=True,
            credential_custody_approved=True,
            authority_record="ACTA-proof-reference",
        )
        decision = evaluate_route(profile, Classification.HIGH_NOFORN)
        self.assertTrue(decision.eligible)
        self.assertEqual(decision.status, "ELIGIBLE")

    def test_non_us_model_origin_is_a_hard_denial(self) -> None:
        base = replace(
            DEVELOPMENT_ROUTE,
            us_person_admin_only=True,
            us_person_user_only=True,
            credential_custody_approved=True,
            authority_record="proof",
        )
        decision = evaluate_route(
            replace(base, model_developer_country="unknown"),
            Classification.HIGH_NOFORN,
        )
        self.assertFalse(decision.eligible)
        self.assertTrue(any("U.S.-origin" in reason for reason in decision.reasons))


if __name__ == "__main__":
    unittest.main()
