"""Dependency-free local API for the NemaShells native application."""

from __future__ import annotations

import json
import re
import uuid
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from . import __version__
from .adapters import adapter_from_environment
from .contracts import BrainRequest
from .policy import Classification, DEVELOPMENT_ROUTE, evaluate_route
from .storage import (
    StateStore,
    StorageUnavailableError,
    state_store_from_environment,
)


def _now() -> str:
    return datetime.now(UTC).isoformat()


class RuntimeState:
    """Orchestrate policy, brain calls, and a provider-neutral state store."""

    def __init__(self, store: StateStore | None = None) -> None:
        self._store = store or state_store_from_environment()
        self._adapter = adapter_from_environment()

    def list_threads(self) -> list[dict[str, Any]]:
        return self._store.list_threads()

    def create_thread(self, title: str) -> dict[str, Any]:
        return self._store.create_thread(title)

    def add_turn(
        self, thread_id: str, text: str, classification: Classification
    ) -> tuple[HTTPStatus, dict[str, Any]]:
        decision = evaluate_route(DEVELOPMENT_ROUTE, classification)
        if not decision.eligible:
            return HTTPStatus.FORBIDDEN, {
                "error": "route_blocked",
                "decision": decision.to_dict(),
            }
        if not self._store.thread_exists(thread_id):
            return HTTPStatus.NOT_FOUND, {"error": "thread_not_found"}
        response = self._adapter.generate(
            BrainRequest(
                request_id=str(uuid.uuid4()),
                messages=({"role": "user", "content": text},),
                authority_context={"classification": classification.value},
            )
        )
        if response.error:
            return HTTPStatus.BAD_GATEWAY, {
                "error": response.error.code,
                "message": response.error.message,
                "retryable": response.error.retryable,
            }
        turn = {
            "id": str(uuid.uuid4()),
            "created_at": _now(),
            "classification": classification.value,
            "operator": text,
            "assistant": response.text,
            "route": response.provenance.route,
        }
        self._store.append_turn(thread_id, turn)
        return HTTPStatus.CREATED, turn

    @property
    def storage_status(self) -> dict[str, Any]:
        return {
            "backend": self._store.backend_id,
            "durable": self._store.durable,
            "credential_exposed_to_model": False,
        }


STATE = RuntimeState()


def operator_state() -> dict[str, Any]:
    noforn = evaluate_route(DEVELOPMENT_ROUTE, Classification.HIGH_NOFORN)
    return {
        "service": {
            "name": "METAXIS",
            "version": __version__,
            "status": "HEALTHY",
            "profile": "orbstack-development",
            "transport": "loopback-only",
        },
        "application": {
            "name": "NemaShells",
            "surface": "native-installed-app",
            "browser_required": False,
        },
        "operator_context": {"cadence": "5.6 sol", "authority_effect": "none"},
        "classification": {
            "requested": Classification.HIGH_NOFORN.value,
            "status": noforn.status,
            "reasons": list(noforn.reasons),
        },
        "model": {
            "primary_candidate": "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16",
            "sufficiency": "EVALUATION-REQUIRED",
            "active_route": STATE._adapter.adapter_id,
            "external_api_allowed": False,
        },
        "proof": {
            "posture": "manual-placeholder",
            "production": False,
            "high_noforn_processing": False,
        },
        "storage": STATE.storage_status,
        "next_safe_action": (
            "Use synthetic or public development data while the approved "
            "Proxmox/U.S.-person-controlled inference profile is built and accepted."
        ),
        "requirements": list(noforn.requirement_ids)
        + [
            "YKS-REQ-MTX-040",
            "YKS-REQ-MTX-BRAIN-003",
            "YKS-REQ-MTX-053",
            "YKS-REQ-MTX-UI-001",
            "YKS-REQ-MTX-UI-002",
            "YKS-REQ-MTX-UI-003",
        ],
    }


class MetaxisHandler(BaseHTTPRequestHandler):
    server_version = "METAXIS/0.1"

    def log_message(self, format: str, *args: Any) -> None:
        # The service logs request metadata only; never prompt contents.
        print(f"{self.log_date_time_string()} {self.address_string()} {format % args}")

    def _send(self, status: HTTPStatus, value: Any) -> None:
        payload = json.dumps(value, separators=(",", ":")).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(payload)

    def _json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 1_048_576:
            raise ValueError("request body exceeds 1 MiB")
        value = json.loads(self.rfile.read(length) or b"{}")
        if not isinstance(value, dict):
            raise ValueError("request body must be a JSON object")
        return value

    def do_GET(self) -> None:  # noqa: N802
        try:
            if self.path == "/healthz":
                self._send(HTTPStatus.OK, {"status": "ok", "version": __version__})
            elif self.path == "/api/v1/operator-state":
                self._send(HTTPStatus.OK, operator_state())
            elif self.path == "/api/v1/threads":
                self._send(HTTPStatus.OK, {"threads": STATE.list_threads()})
            else:
                self._send(HTTPStatus.NOT_FOUND, {"error": "not_found"})
        except StorageUnavailableError:
            self._send(
                HTTPStatus.SERVICE_UNAVAILABLE,
                {"error": "state_store_unavailable", "retryable": True},
            )

    def do_POST(self) -> None:  # noqa: N802
        try:
            value = self._json_body()
            if self.path == "/api/v1/threads":
                thread = STATE.create_thread(str(value.get("title", "")))
                self._send(HTTPStatus.CREATED, thread)
                return
            match = re.fullmatch(r"/api/v1/threads/([^/]+)/turns", self.path)
            if match:
                classification = Classification(
                    str(value.get("classification", Classification.DEVELOPMENT.value))
                )
                status, response = STATE.add_turn(
                    match.group(1), str(value.get("text", "")), classification
                )
                self._send(status, response)
                return
            self._send(HTTPStatus.NOT_FOUND, {"error": "not_found"})
        except (ValueError, json.JSONDecodeError) as error:
            self._send(HTTPStatus.BAD_REQUEST, {"error": "bad_request", "message": str(error)})
        except StorageUnavailableError:
            self._send(
                HTTPStatus.SERVICE_UNAVAILABLE,
                {"error": "state_store_unavailable", "retryable": True},
            )


def make_server(host: str = "127.0.0.1", port: int = 4310) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), MetaxisHandler)


def serve(host: str = "127.0.0.1", port: int = 4310) -> None:
    server = make_server(host, port)
    print(f"METAXIS listening on http://{host}:{server.server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
