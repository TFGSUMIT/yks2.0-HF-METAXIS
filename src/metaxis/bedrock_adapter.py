"""Amazon Bedrock adapter with assumed-role and cost gates."""

from __future__ import annotations

import configparser
import json
import math
import os
import time
from dataclasses import dataclass
from typing import Any, Mapping

from .contracts import (
    BrainError,
    BrainProvenance,
    BrainRequest,
    BrainResponse,
    ToolCall,
)
from .policy import Classification, RouteProfile, evaluate_route
from .secret_file import read_secret_file


EXPECTED_ROLE_NAME = "METAXISBedrockDevelopmentRole"
DEFAULT_MODEL_ID = "nvidia.nemotron-super-3-120b"
DEFAULT_REPOSITORY = "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16"
DEFAULT_REVISION = "d51eab0d1f979ebc26b546e634a04f450d99158e"


@dataclass(frozen=True, slots=True)
class BedrockConfig:
    region: str
    model_id: str
    route: RouteProfile
    max_output_tokens: int = 4096
    max_input_chars: int = 100_000
    max_request_cost_usd: float = 0.01
    input_price_per_million: float = 0.15
    output_price_per_million: float = 0.65
    runtime_version: str = "boto3/registered"


def read_assumed_role_credentials(path_value: str) -> dict[str, str]:
    """Read a bounded INI file and reject credentials not issued to our role."""

    raw = read_secret_file(
        path_value,
        "METAXIS_AWS_CREDENTIALS_FILE",
        max_bytes=8192,
    )
    parser = configparser.ConfigParser(interpolation=None)
    try:
        parser.read_string(raw)
    except configparser.Error as error:
        raise ValueError("METAXIS_AWS_CREDENTIALS_FILE is not valid INI") from error
    section = "metaxis-bedrock"
    if not parser.has_section(section):
        raise ValueError("METAXIS_AWS_CREDENTIALS_FILE lacks metaxis-bedrock profile")
    values = parser[section]
    principal = values.get("x_metaxis_principal_arn", "")
    marker = f":assumed-role/{EXPECTED_ROLE_NAME}/"
    if marker not in principal:
        raise ValueError("AWS credentials were not issued to the METAXIS Bedrock role")
    required = ("aws_access_key_id", "aws_secret_access_key", "aws_session_token")
    if any(not values.get(name, "").strip() for name in required):
        raise ValueError("AWS assumed-role credentials are incomplete")
    return {name: values[name].strip() for name in required}


class BedrockAdapter:
    """Normalize Bedrock Converse responses behind the brain contract."""

    def __init__(self, config: BedrockConfig, client: Any) -> None:
        self.config = config
        self._client = client

    @property
    def adapter_id(self) -> str:
        return self.config.route.route_id

    def _provenance(self) -> BrainProvenance:
        return BrainProvenance(
            provider=self.config.route.provider,
            model_repository=self.config.route.model_repository,
            model_revision=self.config.route.model_revision,
            runtime="amazon-bedrock-converse",
            runtime_version=self.config.runtime_version,
            route=self.config.route.route_id,
        )

    def _estimated_max_cost(self, request: BrainRequest) -> float:
        characters = sum(len(str(message.get("content", ""))) for message in request.messages)
        characters += len(json.dumps(list(request.tools), separators=(",", ":")))
        estimated_input_tokens = math.ceil(characters / 3)
        return (
            estimated_input_tokens * self.config.input_price_per_million
            + request.max_output_tokens * self.config.output_price_per_million
        ) / 1_000_000

    def generate(self, request: BrainRequest) -> BrainResponse:
        raw_classification = str(
            request.authority_context.get(
                "classification", Classification.DEVELOPMENT.value
            )
        )
        try:
            classification = Classification(raw_classification)
        except ValueError:
            classification = Classification.HIGH_NOFORN
        decision = evaluate_route(self.config.route, classification)
        provenance = self._provenance()
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
        input_characters = sum(
            len(str(message.get("content", ""))) for message in request.messages
        )
        if input_characters > self.config.max_input_chars:
            return BrainResponse(
                request_id=request.request_id,
                text="",
                provenance=provenance,
                error=BrainError(
                    code="quota_exceeded",
                    message="request exceeds the registered input-character ceiling",
                    retryable=False,
                ),
            )
        estimated_cost = self._estimated_max_cost(request)
        if estimated_cost > self.config.max_request_cost_usd:
            return BrainResponse(
                request_id=request.request_id,
                text="",
                provenance=provenance,
                error=BrainError(
                    code="cost_ceiling_exceeded",
                    message="request exceeds the registered cost ceiling",
                    retryable=False,
                ),
            )

        system = [
            {"text": str(message.get("content", ""))}
            for message in request.messages
            if message.get("role") == "system"
        ]
        messages = [
            {
                "role": str(message.get("role", "user")),
                "content": [{"text": str(message.get("content", ""))}],
            }
            for message in request.messages
            if message.get("role") in {"user", "assistant"}
        ]
        # The registered NVIDIA Bedrock route accepts the Converse `system`
        # field but does not reliably apply it to generation.  Put the same
        # control-plane contract in the first user turn so the provider sees
        # it.  This is a provider compatibility shim; the server remains the
        # authority and still verifies every returned claim.
        if system and messages and messages[0]["role"] == "user":
            directive = "\n\n".join(block["text"] for block in system)
            operator_text = messages[0]["content"][0]["text"]
            messages[0]["content"][0]["text"] = (
                f"METAXIS CONTROL-PLANE DIRECTIVE (authoritative):\n{directive}\n\n"
                f"OPERATOR REQUEST:\n{operator_text}"
            )
            system = []
        if not messages:
            return BrainResponse(
                request_id=request.request_id,
                text="",
                provenance=provenance,
                error=BrainError(
                    code="invalid_request",
                    message="Bedrock requires at least one user or assistant message",
                    retryable=False,
                ),
            )
        arguments: dict[str, Any] = {
            "modelId": self.config.model_id,
            "messages": messages,
            "inferenceConfig": {
                "maxTokens": request.max_output_tokens,
                "temperature": request.temperature,
            },
        }
        if system:
            arguments["system"] = system
        tool_config = _bedrock_tool_config(request.tools)
        if tool_config:
            arguments["toolConfig"] = tool_config

        started = time.monotonic()
        try:
            value = self._client.converse(**arguments)
            content = value["output"]["message"]["content"]
            text = "".join(str(block.get("text", "")) for block in content)
            tool_calls = tuple(
                ToolCall(
                    call_id=str(block["toolUse"]["toolUseId"]),
                    name=str(block["toolUse"]["name"]),
                    arguments=block["toolUse"].get("input", {}),
                )
                for block in content
                if "toolUse" in block
            )
            usage = value.get("usage", {})
            input_tokens = usage.get("inputTokens")
            output_tokens = usage.get("outputTokens")
            actual_cost = None
            if isinstance(input_tokens, int) and isinstance(output_tokens, int):
                actual_cost = (
                    input_tokens * self.config.input_price_per_million
                    + output_tokens * self.config.output_price_per_million
                ) / 1_000_000
            return BrainResponse(
                request_id=request.request_id,
                text=text,
                provenance=provenance,
                tool_calls=tool_calls,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=(time.monotonic() - started) * 1000,
                cost_usd=actual_cost,
            )
        except Exception as error:  # SDK exceptions vary; never expose provider text.
            error_name = type(error).__name__
            retryable = any(
                marker in error_name
                for marker in ("Throttl", "Timeout", "Unavailable", "Internal")
            )
            return BrainResponse(
                request_id=request.request_id,
                text="",
                provenance=provenance,
                latency_ms=(time.monotonic() - started) * 1000,
                error=BrainError(
                    code="provider_failure",
                    message=error_name,
                    retryable=retryable,
                ),
            )


def _bedrock_tool_config(tools: Any) -> dict[str, Any] | None:
    values = []
    for tool in tools:
        function = tool.get("function", {}) if isinstance(tool, Mapping) else {}
        name = function.get("name")
        schema = function.get("parameters")
        if not isinstance(name, str) or not name or not isinstance(schema, Mapping):
            continue
        spec: dict[str, Any] = {
            "name": name,
            "inputSchema": {"json": dict(schema)},
        }
        description = function.get("description")
        if isinstance(description, str) and description:
            spec["description"] = description
        values.append({"toolSpec": spec})
    return {"tools": values} if values else None


def adapter_from_bedrock_environment() -> BedrockAdapter:
    path = os.environ.get("METAXIS_AWS_CREDENTIALS_FILE", "").strip()
    if not path:
        raise ValueError("METAXIS_AWS_CREDENTIALS_FILE is required")
    credentials = read_assumed_role_credentials(path)
    region = os.environ.get("METAXIS_AWS_REGION", "us-east-1").strip()
    model_id = os.environ.get("METAXIS_BEDROCK_MODEL_ID", DEFAULT_MODEL_ID).strip()
    if region != "us-east-1":
        raise ValueError("Bedrock DEVELOPMENT region must be us-east-1")
    if model_id != DEFAULT_MODEL_ID:
        raise ValueError("unregistered Bedrock model ID")

    import boto3

    client = boto3.client(
        "bedrock-runtime",
        region_name=region,
        aws_access_key_id=credentials["aws_access_key_id"],
        aws_secret_access_key=credentials["aws_secret_access_key"],
        aws_session_token=credentials["aws_session_token"],
    )
    route = RouteProfile(
        route_id="aws-bedrock-super-development",
        provider="aws-bedrock",
        model_repository=os.environ.get("METAXIS_BRAIN_MODEL", DEFAULT_REPOSITORY),
        model_revision=os.environ.get("METAXIS_BRAIN_REVISION", DEFAULT_REVISION),
        model_developer_country="US",
        runtime="amazon-bedrock-converse",
        placement="aws-us-east-1-provider-managed",
        us_person_admin_only=False,
        us_person_user_only=False,
        us_location_only=True,
        egress_default_deny=False,
        external_telemetry_disabled=False,
        credential_custody_approved=False,
        authority_record=None,
    )
    return BedrockAdapter(
        BedrockConfig(
            region=region,
            model_id=model_id,
            route=route,
            max_output_tokens=int(
                os.environ.get("METAXIS_BRAIN_MAX_OUTPUT_TOKENS", "4096")
            ),
            max_input_chars=int(
                os.environ.get("METAXIS_BRAIN_MAX_INPUT_CHARS", "100000")
            ),
            max_request_cost_usd=float(
                os.environ.get("METAXIS_BRAIN_MAX_REQUEST_COST_USD", "0.01")
            ),
            runtime_version=f"boto3/{boto3.__version__}",
        ),
        client,
    )
