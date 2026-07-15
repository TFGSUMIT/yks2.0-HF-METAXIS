"""LECTOR's provider-neutral retrieval and context-delivery boundary."""

from .contracts import (
    ContextItem,
    ContextRequest,
    ContextResponse,
    RetrievalAuthority,
    SourceChunk,
    SourceRecord,
)
from .service import InMemoryLector

__all__ = [
    "ContextItem",
    "ContextRequest",
    "ContextResponse",
    "InMemoryLector",
    "RetrievalAuthority",
    "SourceChunk",
    "SourceRecord",
]
