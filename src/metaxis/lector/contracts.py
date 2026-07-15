"""Provider-neutral contracts for the LECTOR retrieval service.

LECTOR retrieves governed context for EXARTYSIS. It does not execute tools,
own durable authority, or expose a direct NemaShells operator surface.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, Protocol, Sequence, runtime_checkable


def _require_text(**values: str) -> None:
    missing = [name for name, value in values.items() if not value.strip()]
    if missing:
        raise ValueError(f"fields must be non-empty: {', '.join(missing)}")


@dataclass(frozen=True, slots=True)
class SourceRecord:
    """Immutable source metadata required for governed context delivery."""

    source_id: str
    canonical_uri: str
    version: str
    content_hash: str
    license_ref: str
    classification: str
    allowed_use: str
    owner: str
    freshness_at: str

    def __post_init__(self) -> None:
        _require_text(
            source_id=self.source_id,
            canonical_uri=self.canonical_uri,
            version=self.version,
            content_hash=self.content_hash,
            license_ref=self.license_ref,
            classification=self.classification,
            allowed_use=self.allowed_use,
            owner=self.owner,
            freshness_at=self.freshness_at,
        )


@dataclass(frozen=True, slots=True)
class SourceChunk:
    """One normalized source fragment eligible for deterministic retrieval."""

    source: SourceRecord
    chunk_id: str
    content: str
    citation: str

    def __post_init__(self) -> None:
        _require_text(chunk_id=self.chunk_id, content=self.content, citation=self.citation)


@dataclass(frozen=True, slots=True)
class RetrievalAuthority:
    """AXIS-supplied eligibility decision required before retrieval begins."""

    authority_id: str
    eligible_source_ids: FrozenSet[str]

    def __post_init__(self) -> None:
        _require_text(authority_id=self.authority_id)
        if not self.eligible_source_ids:
            raise ValueError("eligible_source_ids must be non-empty")
        if any(not source_id.strip() for source_id in self.eligible_source_ids):
            raise ValueError("eligible_source_ids must not contain blank values")


@dataclass(frozen=True, slots=True)
class ContextRequest:
    """A bounded request for LECTOR-delivered context from EXARTYSIS."""

    request_id: str
    query: str
    authority: RetrievalAuthority
    max_results: int = 5
    context_budget_chars: int = 6000

    def __post_init__(self) -> None:
        _require_text(request_id=self.request_id, query=self.query)
        if not 1 <= self.max_results <= 50:
            raise ValueError("max_results must be between 1 and 50")
        if not 1 <= self.context_budget_chars <= 100_000:
            raise ValueError("context_budget_chars must be between 1 and 100000")


@dataclass(frozen=True, slots=True)
class ContextItem:
    """Delivered context with the evidence needed to inspect or replay it."""

    source_id: str
    source_version: str
    content_hash: str
    chunk_id: str
    content: str
    citation: str
    freshness_at: str
    score: int


@dataclass(frozen=True, slots=True)
class ContextResponse:
    """A bounded retrieval result; denials are explicit and never invented."""

    request_id: str
    authority_id: str
    adapter_id: str
    status: str
    items: Sequence[ContextItem] = field(default_factory=tuple)
    denials: Sequence[str] = field(default_factory=tuple)


@runtime_checkable
class LectorAdapter(Protocol):
    """Replaceable retrieval/index boundary; it cannot execute actions or tools."""

    @property
    def adapter_id(self) -> str:
        """Stable adapter identifier for evidence and replay."""

    def retrieve(self, request: ContextRequest) -> ContextResponse:
        """Return governed, provenance-bearing context or an explicit denial."""
