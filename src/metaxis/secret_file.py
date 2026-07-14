"""Small fail-closed helper for credentials mounted as read-only files."""

from __future__ import annotations

import stat
from pathlib import Path


def read_secret_file(path_value: str, variable: str, *, max_bytes: int = 4096) -> str:
    """Read a bounded owner-only secret file without returning its path or value."""

    path = Path(path_value).expanduser()
    if not path.is_absolute():
        raise ValueError(f"{variable} must be an absolute path")
    if not path.is_file():
        raise ValueError(f"{variable} is not a regular file")
    metadata = path.stat()
    if metadata.st_size > max_bytes:
        raise ValueError(f"{variable} exceeds {max_bytes} bytes")
    if stat.S_IMODE(metadata.st_mode) & 0o077:
        raise ValueError(f"{variable} must not be group/world accessible")
    secret = path.read_text(encoding="utf-8").strip()
    if not secret:
        raise ValueError(f"{variable} is empty")
    return secret
