"""Deterministic model-route admission policy.

Model output never decides whether a route is eligible. Missing control facts
are denials, and development mode never authorizes HIGH/NOFORN processing.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any, Mapping


class Classification(StrEnum):
    PUBLIC = "PUBLIC"
    DEVELOPMENT = "DEVELOPMENT"
    HIGH_NOFORN = "HIGH/NOFORN"


@dataclass(frozen=True, slots=True)
class RouteProfile:
    route_id: str
    provider: str
    model_repository: str
    model_revision: str
    model_developer_country: str
    runtime: str
    placement: str
    us_person_admin_only: bool
    us_person_user_only: bool
    us_location_only: bool
    egress_default_deny: bool
    external_telemetry_disabled: bool
    credential_custody_approved: bool
    authority_record: str | None = None


@dataclass(frozen=True, slots=True)
class RouteDecision:
    route_id: str
    classification: Classification
    eligible: bool
    status: str
    reasons: tuple[str, ...]
    requirement_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["classification"] = self.classification.value
        return value


NOFORN_REQUIREMENTS = (
    "YKS-REQ-MTX-026",
    "YKS-REQ-MTX-BRAIN-018",
    "YKS-REQ-MTX-BRAIN-019",
    "YKS-REQ-MTX-BRAIN-020",
    "YKS-REQ-MTX-BRAIN-021",
)


def evaluate_route(
    profile: RouteProfile, classification: Classification
) -> RouteDecision:
    """Return a fail-closed eligibility decision for one model route."""

    if classification is not Classification.HIGH_NOFORN:
        return RouteDecision(
            route_id=profile.route_id,
            classification=classification,
            eligible=True,
            status="ELIGIBLE-DEVELOPMENT-ONLY",
            reasons=("route is limited to synthetic/public development data",),
            requirement_ids=NOFORN_REQUIREMENTS,
        )

    reasons: list[str] = []
    if profile.model_developer_country != "US":
        reasons.append("model developer provenance is not approved U.S.-origin")
    if not profile.us_person_admin_only:
        reasons.append("administrative access is not restricted to U.S. persons")
    if not profile.us_person_user_only:
        reasons.append("workload access is not restricted to U.S. persons")
    if not profile.us_location_only:
        reasons.append("compute and data placement are not restricted to approved U.S. locations")
    if not profile.egress_default_deny:
        reasons.append("network egress is not deny-by-default")
    if not profile.external_telemetry_disabled:
        reasons.append("external telemetry is not disabled")
    if not profile.credential_custody_approved:
        reasons.append("credential custody is not approved")
    if not profile.authority_record:
        reasons.append("HIGH/NOFORN authority record is absent")

    return RouteDecision(
        route_id=profile.route_id,
        classification=classification,
        eligible=not reasons,
        status="ELIGIBLE" if not reasons else "BLOCKED",
        reasons=tuple(reasons) if reasons else ("all HIGH/NOFORN controls are accepted",),
        requirement_ids=NOFORN_REQUIREMENTS,
    )


def route_profile_from_mapping(value: Mapping[str, Any]) -> RouteProfile:
    """Construct a strict profile without truthy string coercion."""

    boolean_fields = (
        "us_person_admin_only",
        "us_person_user_only",
        "us_location_only",
        "egress_default_deny",
        "external_telemetry_disabled",
        "credential_custody_approved",
    )
    for field in boolean_fields:
        if not isinstance(value.get(field), bool):
            raise ValueError(f"{field} must be a JSON boolean")
    return RouteProfile(**{field: value.get(field) for field in RouteProfile.__dataclass_fields__})


DEVELOPMENT_ROUTE = RouteProfile(
    route_id="mock-local-development",
    provider="metaxis",
    model_repository="local/mock-brain",
    model_revision="deterministic-v1",
    model_developer_country="US",
    runtime="metaxis-mock",
    placement="orbstack-protos3-loopback",
    us_person_admin_only=False,
    us_person_user_only=False,
    us_location_only=True,
    egress_default_deny=True,
    external_telemetry_disabled=True,
    credential_custody_approved=False,
    authority_record=None,
)
