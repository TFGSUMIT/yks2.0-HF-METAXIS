"""Brain adapters with deterministic route admission ahead of network I/O."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from .contracts import BrainError, BrainProvenance, BrainRequest, BrainResponse
from .policy import Classification, RouteProfile, evaluate_route
from .secret_file import read_secret_file


@dataclass(frozen=True, slots=True)
class APIBackendConfig:
    endpoint: str
    api_key: str
    route: RouteProfile
    max_output_tokens: int = 4096
    timeout_seconds: float = 60.0


class MockBrainAdapter:
    @property
    def adapter_id(self) -> str:
        return "mock-local-development"

    def generate(self, request: BrainRequest) -> BrainResponse:
        return BrainResponse(
            request_id=request.request_id,
            text=(
                "NemaShells development route received the turn. No external "
                "model was called and no consequential action was authorized."
            ),
            provenance=BrainProvenance(
                provider="metaxis",
                model_repository="local/mock-brain",
                model_revision="deterministic-v1",
                runtime="metaxis-mock",
                runtime_version="1",
                route=self.adapter_id,
            ),
        )


class OpenAICompatibleAdapter:
    """Minimal transport adapter for approved hosted or self-hosted APIs."""

    def __init__(self, config: APIBackendConfig) -> None:
        self.config = config

    @property
    def adapter_id(self) -> str:
        return self.config.route.route_id

    def generate(self, request: BrainRequest) -> BrainResponse:
        raw_classification = str(
            request.authority_context.get("classification", Classification.DEVELOPMENT.value)
        )
        try:
            classification = Classification(raw_classification)
        except ValueError:
            classification = Classification.HIGH_NOFORN
        decision = evaluate_route(self.config.route, classification)
        provenance = BrainProvenance(
            provider=self.config.route.provider,
            model_repository=self.config.route.model_repository,
            model_revision=self.config.route.model_revision,
            runtime=self.config.route.runtime,
            runtime_version="registered-external",
            route=self.config.route.route_id,
        )
        if not decision.eligible:
            return BrainResponse(
                request_id=request.request_id,
                text="",
                provenance=provenance,
                error=BrainError(
                    code="route_blocked",
                    message="; ".join(decision.reasons),
                    retryable=False,
                ),
            )
        if request.max_output_tokens > self.config.max_output_tokens:
            return BrainResponse(
                request_id=request.request_id,
                text="",
                provenance=provenance,
                error=BrainError(
                    code="quota_exceeded",
                    message="request exceeds the registered output-token ceiling",
                    retryable=False,
                ),
            )

        payload: dict[str, Any] = {
            "model": self.config.route.model_repository,
            "messages": list(request.messages),
            "max_tokens": request.max_output_tokens,
            "temperature": request.temperature,
        }
        if request.tools:
            payload["tools"] = list(request.tools)
        http_request = urllib.request.Request(
            self.config.endpoint.rstrip("/") + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "METAXIS/0.1",
            },
            method="POST",
        )
        started = time.monotonic()
        try:
            with urllib.request.urlopen(
                http_request, timeout=self.config.timeout_seconds
            ) as response:
                value = json.load(response)
            text = str(value["choices"][0]["message"].get("content", ""))
            usage = value.get("usage", {})
            return BrainResponse(
                request_id=request.request_id,
                text=text,
                provenance=provenance,
                input_tokens=usage.get("prompt_tokens"),
                output_tokens=usage.get("completion_tokens"),
                latency_ms=(time.monotonic() - started) * 1000,
            )
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError, IndexError) as error:
            return BrainResponse(
                request_id=request.request_id,
                text="",
                provenance=provenance,
                latency_ms=(time.monotonic() - started) * 1000,
                error=BrainError(
                    code="provider_failure",
                    message=type(error).__name__,
                    retryable=True,
                ),
            )


def adapter_from_environment():
    """Return mock by default; external routing requires explicit complete config."""

    if os.environ.get("METAXIS_BRAIN_MODE", "mock") != "openai-compatible":
        return MockBrainAdapter()
    if os.environ.get("METAXIS_EXTERNAL_MODEL_CALLS") != "1":
        return MockBrainAdapter()
    endpoint = os.environ.get("METAXIS_BRAIN_URL", "").strip()
    api_key_file = os.environ.get("METAXIS_BRAIN_API_KEY_FILE", "").strip()
    api_key = (
        read_secret_file(api_key_file, "METAXIS_BRAIN_API_KEY_FILE")
        if api_key_file
        else os.environ.get("METAXIS_BRAIN_API_KEY", "").strip()
    )
    if not endpoint or not api_key:
        return MockBrainAdapter()
    route = RouteProfile(
        route_id=os.environ.get("METAXIS_BRAIN_ROUTE_ID", "registered-api"),
        provider=os.environ.get("METAXIS_BRAIN_PROVIDER", "registered-provider"),
        model_repository=os.environ.get("METAXIS_BRAIN_MODEL", "registered-model"),
        model_revision=os.environ.get("METAXIS_BRAIN_REVISION", "unregistered"),
        model_developer_country=os.environ.get("METAXIS_BRAIN_DEVELOPER_COUNTRY", "unknown"),
        runtime="openai-compatible-api",
        placement=os.environ.get("METAXIS_BRAIN_PLACEMENT", "unknown"),
        us_person_admin_only=os.environ.get("METAXIS_BRAIN_US_PERSON_ADMIN_ONLY") == "1",
        us_person_user_only=os.environ.get("METAXIS_BRAIN_US_PERSON_USER_ONLY") == "1",
        us_location_only=os.environ.get("METAXIS_BRAIN_US_LOCATION_ONLY") == "1",
        egress_default_deny=os.environ.get("METAXIS_BRAIN_EGRESS_DEFAULT_DENY") == "1",
        external_telemetry_disabled=os.environ.get("METAXIS_BRAIN_EXTERNAL_TELEMETRY_DISABLED") == "1",
        credential_custody_approved=os.environ.get("METAXIS_BRAIN_CUSTODY_APPROVED") == "1",
        authority_record=os.environ.get("METAXIS_HIGH_NOFORN_AUTHORITY_RECORD") or None,
    )
    return OpenAICompatibleAdapter(
        APIBackendConfig(
            endpoint=endpoint,
            api_key=api_key,
            route=route,
            max_output_tokens=int(os.environ.get("METAXIS_BRAIN_MAX_OUTPUT_TOKENS", "4096")),
            timeout_seconds=float(os.environ.get("METAXIS_BRAIN_TIMEOUT_SECONDS", "60")),
        )
    )
