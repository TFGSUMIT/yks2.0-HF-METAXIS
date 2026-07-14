"""Fail-closed, read-only GitHub metadata broker for local operator readback."""

from __future__ import annotations

import json
import os
import re
import stat
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable


JsonOpener = Callable[..., Any]


def _read_token_file(path_value: str) -> str:
    path = Path(path_value).expanduser()
    if not path.is_absolute():
        raise ValueError("METAXIS_GITHUB_TOKEN_FILE must be an absolute path")
    if not path.is_file():
        raise ValueError("METAXIS_GITHUB_TOKEN_FILE is not a regular file")
    if path.stat().st_size > 4096:
        raise ValueError("METAXIS_GITHUB_TOKEN_FILE exceeds 4096 bytes")
    if stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise ValueError("METAXIS_GITHUB_TOKEN_FILE must not be group/world accessible")
    token = path.read_text(encoding="utf-8").strip()
    if not token:
        raise ValueError("METAXIS_GITHUB_TOKEN_FILE is empty")
    return token


def _validate_repo(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value):
        raise ValueError("GitHub repository must use owner/name syntax")
    return value


class GitHubReadBroker:
    """Expose bounded repository metadata without exposing the credential."""

    def __init__(
        self,
        *,
        account: str,
        authority_repo: str,
        implementation_repo: str,
        token: str | None = None,
        api_base: str = "https://api.github.com",
        opener: JsonOpener = urllib.request.urlopen,
        cache_seconds: float = 60.0,
    ) -> None:
        self.account = account
        self.authority_repo = _validate_repo(authority_repo)
        self.implementation_repo = _validate_repo(implementation_repo)
        self._token = token
        self._api_base = api_base.rstrip("/")
        self._opener = opener
        self._cache_seconds = cache_seconds
        self._cache: dict[str, Any] | None = None
        self._cache_at = 0.0
        self._lock = threading.Lock()

    @classmethod
    def from_environment(cls) -> GitHubReadBroker:
        token_file = os.environ.get("METAXIS_GITHUB_TOKEN_FILE", "").strip()
        token = _read_token_file(token_file) if token_file else None
        return cls(
            account=os.environ.get("METAXIS_GITHUB_ACCOUNT", "LittleYeti-Dev"),
            authority_repo=os.environ.get(
                "METAXIS_SOURCE_REPO", "LittleYeti-Dev/yks2.0-ops-hub"
            ),
            implementation_repo=os.environ.get(
                "METAXIS_TARGET_REPO", "LittleYeti-Dev/yks2.0-HF-METAXIS"
            ),
            token=token,
            api_base=os.environ.get("METAXIS_GITHUB_API_BASE", "https://api.github.com"),
        )

    def _base_status(self) -> dict[str, Any]:
        return {
            "account": self.account,
            "authority_repo": self.authority_repo,
            "implementation_repo": self.implementation_repo,
            "mode": "metadata-read-only",
            "credential_configured": self._token is not None,
            "credential_exposed_to_model": False,
            "writes_allowed": False,
        }

    def _get_json(self, path: str) -> dict[str, Any]:
        request = urllib.request.Request(
            self._api_base + path,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self._token}",
                "User-Agent": "METAXIS/0.1",
                "X-GitHub-Api-Version": "2026-03-10",
            },
        )
        with self._opener(request, timeout=10) as response:
            value = json.load(response)
        if not isinstance(value, dict):
            raise ValueError("GitHub response must be an object")
        return value

    def status(self, *, refresh: bool = False) -> dict[str, Any]:
        base = self._base_status()
        if self._token is None:
            return {
                **base,
                "live": False,
                "reason": "credential-not-configured",
                "repositories": [],
            }
        with self._lock:
            if (
                not refresh
                and self._cache is not None
                and time.monotonic() - self._cache_at < self._cache_seconds
            ):
                return dict(self._cache)
            try:
                identity = self._get_json("/user")
                repositories = []
                for full_name in (self.authority_repo, self.implementation_repo):
                    repo = self._get_json(f"/repos/{full_name}")
                    repositories.append(
                        {
                            "full_name": str(repo.get("full_name", full_name)),
                            "private": bool(repo.get("private", False)),
                            "visibility": str(repo.get("visibility", "unknown")),
                            "default_branch": str(repo.get("default_branch", "unknown")),
                            "archived": bool(repo.get("archived", False)),
                            "updated_at": repo.get("updated_at"),
                        }
                    )
                result = {
                    **base,
                    "account": str(identity.get("login", self.account)),
                    "live": True,
                    "reason": "live-read-succeeded",
                    "repositories": repositories,
                }
            except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as error:
                result = {
                    **base,
                    "live": False,
                    "reason": "live-read-failed",
                    "error": type(error).__name__,
                    "repositories": [],
                }
            self._cache = result
            self._cache_at = time.monotonic()
            return dict(result)
