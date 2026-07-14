"""Provider-neutral brain contract for METAXIS Phase 0 research."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable


@dataclass(frozen=True, slots=True)
class ToolCall:
    """A normalized model proposal to invoke a named tool."""

    call_id: str
    name: str
    arguments: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class BrainProvenance:
    """Immutable identifiers required to reproduce an inference result."""

    provider: str
    model_repository: str
    model_revision: str
    runtime: str
    runtime_version: str
    route: str

    def __post_init__(self) -> None:
        values = {
            "provider": self.provider,
            "model_repository": self.model_repository,
            "model_revision": self.model_revision,
            "runtime": self.runtime,
            "runtime_version": self.runtime_version,
            "route": self.route,
        }
        missing = [name for name, value in values.items() if not value.strip()]
        if missing:
            raise ValueError(f"provenance fields must be non-empty: {', '.join(missing)}")


@dataclass(frozen=True, slots=True)
class BrainRequest:
    """Normalized request passed to any METAXIS brain adapter."""

    request_id: str
    messages: Sequence[Mapping[str, str]]
    tools: Sequence[Mapping[str, Any]] = field(default_factory=tuple)
    max_output_tokens: int = 1024
    temperature: float = 0.0
    authority_context: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.request_id.strip():
            raise ValueError("request_id must be non-empty")
        if not self.messages:
            raise ValueError("messages must be non-empty")
        if self.max_output_tokens < 1:
            raise ValueError("max_output_tokens must be positive")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0 and 2")


@dataclass(frozen=True, slots=True)
class BrainError:
    """Normalized provider failure without leaking credentials or raw secrets."""

    code: str
    message: str
    retryable: bool
    provider_status: int | None = None


@dataclass(frozen=True, slots=True)
class BrainResponse:
    """Normalized response from a METAXIS brain adapter."""

    request_id: str
    text: str
    provenance: BrainProvenance
    tool_calls: Sequence[ToolCall] = field(default_factory=tuple)
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: float | None = None
    cost_usd: float | None = None
    error: BrainError | None = None


@runtime_checkable
class BrainAdapter(Protocol):
    """Replaceable inference boundary; authorization remains outside it."""

    @property
    def adapter_id(self) -> str:
        """Stable adapter identifier used in evidence and replay."""

    def generate(self, request: BrainRequest) -> BrainResponse:
        """Generate a normalized response or a normalized failure."""
