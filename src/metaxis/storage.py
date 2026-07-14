"""Provider-neutral dynamic-state stores for METAXIS.

The default in-memory store is development-only.  The Cloudflare D1 adapter
uses the D1 REST query API so the local OrbStack service can keep durable
thread, turn, and state-event records without giving the model credential or
database authority.
"""

from __future__ import annotations

import json
import os
import threading
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Callable, Protocol

from .secret_file import read_secret_file


def _now() -> str:
    return datetime.now(UTC).isoformat()


class StorageConfigurationError(RuntimeError):
    """Raised when an explicitly selected durable backend is incomplete."""


class StorageUnavailableError(RuntimeError):
    """Raised when a configured state authority cannot complete an operation."""


class StateStore(Protocol):
    backend_id: str
    durable: bool

    def list_threads(self) -> list[dict[str, Any]]: ...

    def get_thread(self, thread_id: str) -> dict[str, Any] | None: ...

    def create_thread(self, title: str) -> dict[str, Any]: ...

    def thread_exists(self, thread_id: str) -> bool: ...

    def append_turn(self, thread_id: str, turn: dict[str, Any]) -> None: ...


class MemoryStateStore:
    """Process-local state for deterministic development and test runs."""

    backend_id = "memory-development"
    durable = False

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._threads: dict[str, dict[str, Any]] = {}

    def list_threads(self) -> list[dict[str, Any]]:
        with self._lock:
            return [
                {**thread, "turns": [dict(turn) for turn in thread["turns"]]}
                for thread in self._threads.values()
            ]

    def create_thread(self, title: str) -> dict[str, Any]:
        with self._lock:
            thread_id = str(uuid.uuid4())
            value = {
                "id": thread_id,
                "title": title.strip() or "New task",
                "created_at": _now(),
                "turns": [],
            }
            self._threads[thread_id] = value
            return dict(value)

    def get_thread(self, thread_id: str) -> dict[str, Any] | None:
        with self._lock:
            thread = self._threads.get(thread_id)
            if thread is None:
                return None
            return {
                **thread,
                "turns": [dict(turn) for turn in thread["turns"]],
            }

    def thread_exists(self, thread_id: str) -> bool:
        with self._lock:
            return thread_id in self._threads

    def append_turn(self, thread_id: str, turn: dict[str, Any]) -> None:
        with self._lock:
            if thread_id not in self._threads:
                raise KeyError(thread_id)
            self._threads[thread_id]["turns"].append(dict(turn))


QueryTransport = Callable[[urllib.request.Request, float], dict[str, Any]]


def _urlopen_json(request: urllib.request.Request, timeout: float) -> dict[str, Any]:
    with urllib.request.urlopen(request, timeout=timeout) as response:
        value = json.load(response)
    if not isinstance(value, dict):
        raise StorageUnavailableError("D1 returned a non-object response")
    return value


@dataclass(frozen=True)
class D1Settings:
    account_id: str
    database_id: str
    api_token: str
    timeout_seconds: float = 10.0
    api_base: str = "https://api.cloudflare.com/client/v4"


class CloudflareD1StateStore:
    """Durable dynamic state backed by the Cloudflare D1 query API."""

    backend_id = "cloudflare-d1"
    durable = True

    def __init__(
        self,
        settings: D1Settings,
        transport: QueryTransport = _urlopen_json,
    ) -> None:
        self.settings = settings
        self._transport = transport

    @property
    def _query_url(self) -> str:
        base = self.settings.api_base.rstrip("/")
        return (
            f"{base}/accounts/{self.settings.account_id}/d1/database/"
            f"{self.settings.database_id}/query"
        )

    def _execute(self, statements: list[dict[str, Any]]) -> list[dict[str, Any]]:
        body: dict[str, Any]
        if len(statements) == 1:
            body = statements[0]
        else:
            body = {"batch": statements}
        request = urllib.request.Request(
            self._query_url,
            data=json.dumps(body, separators=(",", ":")).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.settings.api_token}",
                "Content-Type": "application/json",
                "User-Agent": "METAXIS/0.1 D1-state-adapter",
            },
            method="POST",
        )
        try:
            value = self._transport(request, self.settings.timeout_seconds)
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as error:
            raise StorageUnavailableError("Cloudflare D1 request failed") from error
        if value.get("success") is not True:
            raise StorageUnavailableError("Cloudflare D1 rejected the request")
        result = value.get("result")
        if not isinstance(result, list) or not result:
            raise StorageUnavailableError("Cloudflare D1 returned no query result")
        for item in result:
            if not isinstance(item, dict) or item.get("success") is not True:
                raise StorageUnavailableError("Cloudflare D1 query did not succeed")
        return result

    @staticmethod
    def _rows(result: dict[str, Any]) -> list[dict[str, Any]]:
        rows = result.get("results", [])
        if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
            raise StorageUnavailableError("Cloudflare D1 returned invalid rows")
        return rows

    def list_threads(self) -> list[dict[str, Any]]:
        sql = """
            SELECT
                t.id AS thread_id,
                t.title AS thread_title,
                t.created_at AS thread_created_at,
                r.id AS turn_id,
                r.created_at AS turn_created_at,
                r.classification AS turn_classification,
                r.operator_text,
                r.assistant_text,
                r.route
            FROM metaxis_threads AS t
            LEFT JOIN metaxis_turns AS r ON r.thread_id = t.id
            ORDER BY t.created_at ASC, r.created_at ASC
        """
        rows = self._rows(self._execute([{"sql": sql, "params": []}])[0])
        threads: dict[str, dict[str, Any]] = {}
        for row in rows:
            thread_id = str(row["thread_id"])
            thread = threads.setdefault(
                thread_id,
                {
                    "id": thread_id,
                    "title": row["thread_title"],
                    "created_at": row["thread_created_at"],
                    "turns": [],
                },
            )
            if row.get("turn_id") is not None:
                thread["turns"].append(
                    {
                        "id": row["turn_id"],
                        "created_at": row["turn_created_at"],
                        "classification": row["turn_classification"],
                        "operator": row["operator_text"],
                        "assistant": row["assistant_text"],
                        "route": row["route"],
                    }
                )
        return list(threads.values())

    def get_thread(self, thread_id: str) -> dict[str, Any] | None:
        sql = """
            SELECT
                t.id AS thread_id,
                t.title AS thread_title,
                t.created_at AS thread_created_at,
                r.id AS turn_id,
                r.created_at AS turn_created_at,
                r.classification AS turn_classification,
                r.operator_text,
                r.assistant_text,
                r.route
            FROM metaxis_threads AS t
            LEFT JOIN metaxis_turns AS r ON r.thread_id = t.id
            WHERE t.id = ?1
            ORDER BY r.created_at ASC
        """
        rows = self._rows(
            self._execute([{"sql": sql, "params": [thread_id]}])[0]
        )
        if not rows:
            return None
        thread = {
            "id": str(rows[0]["thread_id"]),
            "title": rows[0]["thread_title"],
            "created_at": rows[0]["thread_created_at"],
            "turns": [],
        }
        for row in rows:
            if row.get("turn_id") is not None:
                thread["turns"].append(
                    {
                        "id": row["turn_id"],
                        "created_at": row["turn_created_at"],
                        "classification": row["turn_classification"],
                        "operator": row["operator_text"],
                        "assistant": row["assistant_text"],
                        "route": row["route"],
                    }
                )
        return thread

    def create_thread(self, title: str) -> dict[str, Any]:
        thread_id = str(uuid.uuid4())
        created_at = _now()
        value = {
            "id": thread_id,
            "title": title.strip() or "New task",
            "created_at": created_at,
            "turns": [],
        }
        event_id = str(uuid.uuid4())
        self._execute(
            [
                {
                    "sql": (
                        "INSERT INTO metaxis_threads "
                        "(id, title, created_at, updated_at) VALUES (?1, ?2, ?3, ?3)"
                    ),
                    "params": [thread_id, value["title"], created_at],
                },
                {
                    "sql": (
                        "INSERT INTO metaxis_state_events "
                        "(id, event_type, subject_id, classification, payload_json, created_at) "
                        "VALUES (?1, ?2, ?3, ?4, ?5, ?6)"
                    ),
                    "params": [
                        event_id,
                        "thread.created",
                        thread_id,
                        "DEVELOPMENT",
                        '{"backend":"cloudflare-d1"}',
                        created_at,
                    ],
                },
            ]
        )
        return value

    def thread_exists(self, thread_id: str) -> bool:
        result = self._execute(
            [
                {
                    "sql": "SELECT id FROM metaxis_threads WHERE id = ?1 LIMIT 1",
                    "params": [thread_id],
                }
            ]
        )[0]
        return bool(self._rows(result))

    def append_turn(self, thread_id: str, turn: dict[str, Any]) -> None:
        event_id = str(uuid.uuid4())
        created_at = str(turn["created_at"])
        event_payload = json.dumps(
            {"route": turn["route"], "turn_id": turn["id"]},
            separators=(",", ":"),
            sort_keys=True,
        )
        self._execute(
            [
                {
                    "sql": (
                        "INSERT INTO metaxis_turns "
                        "(id, thread_id, created_at, classification, operator_text, "
                        "assistant_text, route) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)"
                    ),
                    "params": [
                        turn["id"],
                        thread_id,
                        created_at,
                        turn["classification"],
                        turn["operator"],
                        turn["assistant"],
                        turn["route"],
                    ],
                },
                {
                    "sql": "UPDATE metaxis_threads SET updated_at = ?1 WHERE id = ?2",
                    "params": [created_at, thread_id],
                },
                {
                    "sql": (
                        "INSERT INTO metaxis_state_events "
                        "(id, event_type, subject_id, classification, payload_json, created_at) "
                        "VALUES (?1, ?2, ?3, ?4, ?5, ?6)"
                    ),
                    "params": [
                        event_id,
                        "turn.persisted",
                        thread_id,
                        turn["classification"],
                        event_payload,
                        created_at,
                    ],
                },
            ]
        )


def state_store_from_environment() -> StateStore:
    backend = os.environ.get("METAXIS_STATE_BACKEND", "memory").strip().lower()
    if backend in {"", "memory"}:
        return MemoryStateStore()
    if backend != "cloudflare-d1":
        raise StorageConfigurationError(f"unsupported METAXIS_STATE_BACKEND: {backend}")

    token_file = os.environ.get("CLOUDFLARE_D1_API_TOKEN_FILE", "").strip()
    try:
        api_token = (
            read_secret_file(token_file, "CLOUDFLARE_D1_API_TOKEN_FILE")
            if token_file
            else os.environ.get("CLOUDFLARE_D1_API_TOKEN", "").strip()
        )
    except ValueError as error:
        raise StorageConfigurationError(str(error)) from error

    settings = {
        "account_id": os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip(),
        "database_id": os.environ.get("METAXIS_D1_DATABASE_ID", "").strip(),
        "api_token": api_token,
    }
    missing = [name for name, value in settings.items() if not value]
    if missing:
        raise StorageConfigurationError(
            "cloudflare-d1 selected but required settings are missing: "
            + ", ".join(missing)
        )
    timeout = float(os.environ.get("METAXIS_D1_TIMEOUT_SECONDS", "10"))
    api_base = os.environ.get(
        "METAXIS_D1_API_BASE", "https://api.cloudflare.com/client/v4"
    ).strip()
    return CloudflareD1StateStore(
        D1Settings(timeout_seconds=timeout, api_base=api_base, **settings)
    )
