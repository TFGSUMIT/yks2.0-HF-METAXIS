"""Deterministic in-memory LECTOR adapter for public/synthetic pilot fixtures."""

from __future__ import annotations

import re
from collections.abc import Sequence

from .contracts import ContextItem, ContextRequest, ContextResponse, SourceChunk


def _tokens(value: str) -> frozenset[str]:
    return frozenset(re.findall(r"[a-z0-9]+", value.lower()))


class InMemoryLector:
    """A CPU-only comparison adapter, deliberately not a vector/index backend."""

    adapter_id = "in-memory-lexical-development"

    def __init__(self, chunks: Sequence[SourceChunk] = ()) -> None:
        self._chunks = tuple(chunks)
        identities = {(chunk.source.source_id, chunk.chunk_id) for chunk in self._chunks}
        if len(identities) != len(self._chunks):
            raise ValueError("source chunks must have unique source_id/chunk_id pairs")

    def retrieve(self, request: ContextRequest) -> ContextResponse:
        eligible = tuple(
            chunk
            for chunk in self._chunks
            if chunk.source.source_id in request.authority.eligible_source_ids
        )
        if not eligible:
            return ContextResponse(
                request_id=request.request_id,
                authority_id=request.authority.authority_id,
                adapter_id=self.adapter_id,
                status="denied",
                denials=("no registered source is eligible for this authority decision",),
            )

        query_tokens = _tokens(request.query)
        ranked = sorted(
            (
                (len(query_tokens & _tokens(chunk.content)), chunk)
                for chunk in eligible
            ),
            key=lambda value: (-value[0], value[1].source.source_id, value[1].chunk_id),
        )
        matches = tuple((score, chunk) for score, chunk in ranked if score > 0)
        if not matches:
            return ContextResponse(
                request_id=request.request_id,
                authority_id=request.authority.authority_id,
                adapter_id=self.adapter_id,
                status="no_match",
                denials=("no eligible source matched the retrieval query",),
            )

        remaining = request.context_budget_chars
        items: list[ContextItem] = []
        skipped_for_budget = False
        for score, chunk in matches:
            if len(items) >= request.max_results:
                break
            if len(chunk.content) > remaining:
                skipped_for_budget = True
                continue
            remaining -= len(chunk.content)
            items.append(
                ContextItem(
                    source_id=chunk.source.source_id,
                    source_version=chunk.source.version,
                    content_hash=chunk.source.content_hash,
                    chunk_id=chunk.chunk_id,
                    content=chunk.content,
                    citation=chunk.citation,
                    freshness_at=chunk.source.freshness_at,
                    score=score,
                )
            )

        if not items:
            return ContextResponse(
                request_id=request.request_id,
                authority_id=request.authority.authority_id,
                adapter_id=self.adapter_id,
                status="denied",
                denials=("context budget excludes every eligible matching source",),
            )
        denials = ("one or more matches exceeded the context budget",) if skipped_for_budget else ()
        return ContextResponse(
            request_id=request.request_id,
            authority_id=request.authority.authority_id,
            adapter_id=self.adapter_id,
            status="delivered",
            items=tuple(items),
            denials=denials,
        )
