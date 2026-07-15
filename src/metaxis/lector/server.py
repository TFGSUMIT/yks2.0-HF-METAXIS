"""Private, dependency-free HTTP boundary for the CPU-first LECTOR service."""

from __future__ import annotations

import json
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .contracts import ContextRequest, RetrievalAuthority
from .service import InMemoryLector


class LectorHTTPServer(ThreadingHTTPServer):
    """HTTP server carrying an injected adapter for deterministic testability."""

    def __init__(self, address: tuple[str, int], adapter: InMemoryLector) -> None:
        super().__init__(address, LectorHandler)
        self.adapter = adapter


class LectorHandler(BaseHTTPRequestHandler):
    """Expose health and EXARTYSIS context delivery; no tool or operator routes."""

    server: LectorHTTPServer

    def log_message(self, _format: str, *_args: object) -> None:
        """Do not write request payloads to the default HTTP access log."""

    def _reply(self, status: HTTPStatus, value: dict[str, Any]) -> None:
        encoded = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if not 1 <= length <= 128_000:
            raise ValueError("request body must be between 1 and 128000 bytes")
        value = json.loads(self.rfile.read(length))
        if not isinstance(value, dict):
            raise ValueError("request body must be a JSON object")
        return value

    @staticmethod
    def _request_from_json(value: dict[str, Any]) -> ContextRequest:
        authority = value.get("authority")
        if not isinstance(authority, dict):
            raise ValueError("authority must be an object")
        eligible_source_ids = authority.get("eligible_source_ids")
        if not isinstance(eligible_source_ids, list) or not all(
            isinstance(source_id, str) for source_id in eligible_source_ids
        ):
            raise ValueError("authority.eligible_source_ids must be a string array")
        return ContextRequest(
            request_id=str(value.get("request_id", "")),
            query=str(value.get("query", "")),
            authority=RetrievalAuthority(
                authority_id=str(authority.get("authority_id", "")),
                eligible_source_ids=frozenset(eligible_source_ids),
            ),
            max_results=int(value.get("max_results", 5)),
            context_budget_chars=int(value.get("context_budget_chars", 6000)),
        )

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/healthz":
            self._reply(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        self._reply(
            HTTPStatus.OK,
            {
                "status": "ok",
                "service": "lector",
                "adapter": self.server.adapter.adapter_id,
                "operator_routes": "denied",
                "tool_execution": "denied",
            },
        )

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/v1/context":
            self._reply(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        try:
            request = self._request_from_json(self._read_json())
        except (TypeError, ValueError, json.JSONDecodeError) as error:
            self._reply(HTTPStatus.BAD_REQUEST, {"error": "invalid_request", "message": str(error)})
            return
        response = self.server.adapter.retrieve(request)
        self._reply(HTTPStatus.OK, asdict(response))


def make_server(
    adapter: InMemoryLector | None = None, host: str = "127.0.0.1", port: int = 4320
) -> LectorHTTPServer:
    """Build an empty-registry server; fixture registration is explicit."""

    return LectorHTTPServer((host, port), adapter or InMemoryLector())


def serve(host: str = "127.0.0.1", port: int = 4320) -> None:
    server = make_server(host=host, port=port)
    try:
        server.serve_forever()
    finally:
        server.server_close()
