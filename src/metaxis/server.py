"""Dependency-free local API for the NemaShells native application."""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from . import __version__
from .adapters import adapter_from_environment
from .capability_registry import REGISTRY
from .contracts import BrainRequest
from .github_broker import GitHubReadBroker
from .policy import Classification, DEVELOPMENT_ROUTE, evaluate_route
from .storage import (
    StateStore,
    StorageUnavailableError,
    state_store_from_environment,
)
from .verification import (
    ControlPlaneSnapshot,
    DraftParseError,
    ValidationIssue,
    output_contract,
    parse_draft,
    render_blocked,
    render_verified,
    repair_instruction,
    validate_draft,
)


SYSTEM_PROMPT = """You are NemaShells, the conversational surface for the METAXIS provider-neutral agentic harness. This is a DEVELOPMENT-only session. Use only synthetic, public, or explicitly approved non-sensitive information. Never claim HIGH/NOFORN eligibility, production activation, tool execution, GitHub writes, or consequential action. Never request or repeat credentials. State clearly when an operation is unavailable through the current presentation-only surface."""


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _is_yeti_live_trigger(text: str) -> bool:
    normalized = text.strip().lower().replace("’", "'")
    normalized = re.sub(r"[^a-z']+", " ", normalized).strip()
    return normalized in {
        "yeti live",
        "yetis live",
        "yeti's live",
        "yeti's life",
    }


def _yeti_live_brief(
    storage_status: dict[str, Any],
    github_status: dict[str, Any],
    model_route: str,
    capability_status: dict[str, Any],
) -> str:
    github_connection = "live" if github_status["live"] else "declared-only"
    d1_live = (
        storage_status["backend"] == "cloudflare-d1"
        and storage_status["durable"] is True
    )
    if d1_live:
        d1_credential_line = (
            "- D1 adapter credential: active from a read-only file mount; "
            "exposed to the model: never."
        )
        d1_administration_line = (
            "- Project 21, workflow changes, and D1 schema administration remain "
            "on the governed cGunther host path."
        )
    else:
        d1_credential_line = (
            "- D1 adapter credential: absent; durable runtime storage is inactive."
        )
        d1_administration_line = (
            "- Project 21, workflow changes, and D1 activation or administration "
            "require the governed cGunther host path."
        )
    return "\n".join(
        [
            "YKS Ops Live Brief",
            "",
            "1. Control-plane state",
            "- NemaShells Tauri is live on PROTOS-4 through the loopback-only METAXIS service.",
            "- Surface: cGunther-compatible local development shell; authority effect: none.",
            f"- Storage: {storage_status['backend']}; durable: {str(storage_status['durable']).lower()}.",
            "- HIGH/NOFORN remains blocked.",
            "",
            "2. Root roadmap state",
            "- Authority remains YKS Ops root #422 and SAFe chain #474 -> #475 -> #476.",
            "- PROTOS-3 is the Swift lane; PROTOS-4 is the Tauri 2 presentation lane.",
            "",
            "3. CI/CD and automation",
            f"- GitHub broker: {github_connection}; metadata read-only; writes denied.",
            f"- Brain route: {model_route}.",
            f"- Capability pack: {capability_status['active_count']} active / {capability_status['loaded_count']} loaded; writes denied.",
            d1_credential_line,
            d1_administration_line,
            "",
            "4. Canon and architecture drift",
            "- GitHub, D1, and canon remain the durable body; NemaShells is presentation only.",
            "- No external model was called and no consequential action was authorized.",
            "",
            "5. Recommended next ops move",
            "- Continue with synthetic/public DEVELOPMENT work, or activate an approved model route after its gates pass.",
        ]
    )


def _is_github_identity_question(text: str) -> bool:
    normalized = re.sub(r"[^a-z]+", " ", text.strip().lower()).strip()
    return normalized in {
        "what gh are you talking to",
        "what github are you talking to",
        "which gh are you talking to",
        "which github are you talking to",
        "what github are you connected to",
        "which github are you connected to",
    }


def _github_identity_brief(status: dict[str, Any]) -> str:
    live = "live" if status["live"] else "declared-only"
    lines = [
        "GitHub broker readback",
        "",
        f"- Account: {status['account']}",
        f"- Authority repository: {status['authority_repo']}",
        f"- Implementation repository: {status['implementation_repo']}",
        f"- Connection: {live} ({status['reason']})",
        "- Mode: metadata read-only; writes denied.",
        "- Credential exposed to the model: never.",
    ]
    if not status["live"]:
        lines.append(
            "- NemaShells is not making live GitHub calls until a repository-scoped read credential is mounted into the METAXIS broker."
        )
    return "\n".join(lines)


class RuntimeState:
    """Orchestrate policy, brain calls, and a provider-neutral state store."""

    def __init__(
        self,
        store: StateStore | None = None,
        github_broker: GitHubReadBroker | None = None,
    ) -> None:
        self._store = store or state_store_from_environment()
        self._adapter = adapter_from_environment()
        self._github_broker = github_broker or GitHubReadBroker.from_environment()

    def list_threads(self) -> list[dict[str, Any]]:
        return self._store.list_threads()

    def create_thread(self, title: str) -> dict[str, Any]:
        return self._store.create_thread(title)

    def get_thread(self, thread_id: str) -> dict[str, Any] | None:
        return self._store.get_thread(thread_id)

    def _model_repository(self) -> str:
        config = getattr(self._adapter, "config", None)
        route = getattr(config, "route", None)
        repository = getattr(route, "model_repository", None)
        if isinstance(repository, str) and repository.strip():
            return repository
        if self._adapter.adapter_id == "mock-local-development":
            return "local/mock-brain"
        return "unregistered"

    def _control_plane_snapshot(self) -> ControlPlaneSnapshot:
        noforn = evaluate_route(DEVELOPMENT_ROUTE, Classification.HIGH_NOFORN)
        return ControlPlaneSnapshot(
            facts={
                "model.route": self._adapter.adapter_id,
                "model.external_inference": self._adapter.adapter_id
                != "mock-local-development",
                "model.repository": self._model_repository(),
                "storage.backend": self._store.backend_id,
                "storage.durable": self._store.durable,
                "storage.application_writes": True,
                "github.mode": "metadata-read-only",
                "github.writes_allowed": False,
                "classification.high_noforn": noforn.status,
                "actions.consequential_allowed": False,
                "model.tools_available": False,
                "repository.branch_prefix": "codex/",
            },
            approved_action_ids=(),
        )

    def _system_context(self, snapshot: ControlPlaneSnapshot) -> str:
        external = self._adapter.adapter_id != "mock-local-development"
        return "\n".join(
            [
                SYSTEM_PROMPT,
                "",
                "Live non-secret control-plane context for this request:",
                f"- Active brain route: {self._adapter.adapter_id}.",
                f"- This answer uses external inference: {str(external).lower()}.",
                f"- Storage backend: {self._store.backend_id}; durable: {str(self._store.durable).lower()}.",
                "- METAXIS may append DEVELOPMENT thread and turn records. The mounted credential files are read-only; that does not make D1 itself read-only.",
                "- GitHub access is bounded metadata read-only; writes are denied.",
                "- The model has no tools and cannot execute the next action itself.",
                "- HIGH/NOFORN and consequential actions remain blocked.",
                "- Any older statement that no external model was called applies only to that earlier deterministic local-readback turn, not to this request.",
                "",
                output_contract(snapshot),
            ]
        )

    def _brain_messages(
        self,
        thread_id: str,
        text: str,
        snapshot: ControlPlaneSnapshot,
    ) -> tuple[dict[str, str], ...]:
        thread = self._store.get_thread(thread_id)
        if thread is None:
            return ({"role": "user", "content": text},)
        max_turns = max(0, int(os.environ.get("METAXIS_BRAIN_CONTEXT_TURNS", "12")))
        max_chars = max(0, int(os.environ.get("METAXIS_BRAIN_CONTEXT_CHARS", "24000")))
        history: list[dict[str, str]] = []
        characters = len(text)
        for turn in reversed(thread["turns"][-max_turns:] if max_turns else []):
            pair = (
                {"role": "user", "content": str(turn["operator"])},
                {"role": "assistant", "content": str(turn["assistant"])},
            )
            pair_characters = sum(len(message["content"]) for message in pair)
            if characters + pair_characters > max_chars:
                break
            history[0:0] = pair
            characters += pair_characters
        return (
            {"role": "system", "content": self._system_context(snapshot)},
            *history,
            {"role": "user", "content": text},
        )

    @staticmethod
    def _aggregate_brain_evidence(responses: list[Any]) -> dict[str, Any]:
        last = responses[-1]

        def total(field: str) -> int | float | None:
            values = [getattr(response, field) for response in responses]
            if not values or any(value is None for value in values):
                return None
            return sum(values)

        return {
            "provider": last.provenance.provider,
            "model_repository": last.provenance.model_repository,
            "model_revision": last.provenance.model_revision,
            "runtime": last.provenance.runtime,
            "runtime_version": last.provenance.runtime_version,
            "input_tokens": total("input_tokens"),
            "output_tokens": total("output_tokens"),
            "latency_ms": total("latency_ms"),
            "cost_usd": total("cost_usd"),
        }

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
        if _is_yeti_live_trigger(text):
            turn = {
                "id": str(uuid.uuid4()),
                "created_at": _now(),
                "classification": classification.value,
                "operator": text,
                "assistant": _yeti_live_brief(
                    self.storage_status,
                    self.github_status,
                    self._adapter.adapter_id,
                    self.capability_status,
                ),
                "route": "yeti-boot-local-readback",
                "verification": {
                    "status": "VERIFIED-LOCAL",
                    "mode": "deterministic-local-readback",
                    "attempts": 0,
                },
            }
            self._store.append_turn(thread_id, turn)
            return HTTPStatus.CREATED, turn
        if _is_github_identity_question(text):
            turn = {
                "id": str(uuid.uuid4()),
                "created_at": _now(),
                "classification": classification.value,
                "operator": text,
                "assistant": _github_identity_brief(self.github_status),
                "route": "github-readback-local",
                "verification": {
                    "status": "VERIFIED-LOCAL",
                    "mode": "deterministic-local-readback",
                    "attempts": 0,
                },
            }
            self._store.append_turn(thread_id, turn)
            return HTTPStatus.CREATED, turn
        snapshot = self._control_plane_snapshot()
        base_messages = self._brain_messages(thread_id, text, snapshot)
        max_attempts = min(
            3,
            max(1, int(os.environ.get("METAXIS_VERIFICATION_MAX_ATTEMPTS", "2"))),
        )
        max_output_tokens = min(
            2048,
            max(
                256,
                int(os.environ.get("METAXIS_VERIFICATION_MAX_OUTPUT_TOKENS", "1024")),
            ),
        )
        responses: list[Any] = []
        issues: tuple[ValidationIssue, ...] = ()
        messages = base_messages
        for attempt in range(1, max_attempts + 1):
            response = self._adapter.generate(
                BrainRequest(
                    request_id=str(uuid.uuid4()),
                    messages=messages,
                    max_output_tokens=max_output_tokens,
                    authority_context={"classification": classification.value},
                )
            )
            if response.error:
                return HTTPStatus.BAD_GATEWAY, {
                    "error": response.error.code,
                    "message": response.error.message,
                    "retryable": response.error.retryable,
                }
            responses.append(response)

            if self._adapter.adapter_id == "mock-local-development":
                verification = {
                    "status": "VERIFIED-LOCAL",
                    "mode": "deterministic-mock",
                    "attempts": 1,
                    "snapshot_id": snapshot.snapshot_id,
                    "issues": [],
                }
                assistant = response.text
                break

            try:
                candidate = parse_draft(response.text)
            except DraftParseError as error:
                issues = (ValidationIssue("invalid_draft_schema", str(error)),)
            else:
                validation = validate_draft(candidate, snapshot)
                issues = validation.issues
                if validation.valid:
                    verification = {
                        "status": "VERIFIED",
                        "mode": "structured-repair-v1",
                        "attempts": attempt,
                        "snapshot_id": snapshot.snapshot_id,
                        "issues": [],
                    }
                    assistant = render_verified(candidate, snapshot, attempt)
                    break

            if attempt < max_attempts:
                messages = (
                    base_messages[0],
                    {
                        "role": "user",
                        "content": "\n\n".join(
                            (
                                str(base_messages[-1]["content"]),
                                repair_instruction(snapshot, issues),
                            )
                        ),
                    },
                )
        else:
            verification = {
                "status": "BLOCKED",
                "mode": "structured-repair-v1",
                "attempts": max_attempts,
                "snapshot_id": snapshot.snapshot_id,
                "issues": [issue.to_dict() for issue in issues],
            }
            assistant = render_blocked(snapshot, max_attempts, issues)

        last_response = responses[-1]
        turn = {
            "id": str(uuid.uuid4()),
            "created_at": _now(),
            "classification": classification.value,
            "operator": text,
            "assistant": assistant,
            "route": last_response.provenance.route,
            "brain_evidence": self._aggregate_brain_evidence(responses),
            "verification": verification,
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

    @property
    def github_status(self) -> dict[str, Any]:
        return self._github_broker.status()

    @property
    def capability_status(self) -> dict[str, Any]:
        activated_ids: set[str] = set()
        if self._store.backend_id == "cloudflare-d1" and self._store.durable:
            activated_ids.add("cloudflare")
        return REGISTRY.status(activated_ids=activated_ids)


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
            "primary_candidate": "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16",
            "sufficiency": "EVALUATION-REQUIRED",
            "active_route": STATE._adapter.adapter_id,
            "external_api_allowed": STATE._adapter.adapter_id
            != "mock-local-development",
        },
        "verification": {
            "mode": "structured-repair-v1",
            "max_attempts": min(
                3,
                max(
                    1,
                    int(os.environ.get("METAXIS_VERIFICATION_MAX_ATTEMPTS", "2")),
                ),
            ),
            "registered_claims": len(STATE._control_plane_snapshot().facts),
            "write_actions_registered": 0,
        },
        "proof": {
            "posture": "manual-placeholder",
            "production": False,
            "high_noforn_processing": False,
        },
        "storage": STATE.storage_status,
        "capabilities": STATE.capability_status,
        "integrations": {"github": STATE.github_status},
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
            elif self.path == "/api/v1/github-state":
                self._send(HTTPStatus.OK, STATE.github_status)
            elif self.path == "/api/v1/capabilities":
                self._send(HTTPStatus.OK, STATE.capability_status)
            elif self.path == "/api/v1/threads":
                self._send(HTTPStatus.OK, {"threads": STATE.list_threads()})
            elif match := re.fullmatch(r"/api/v1/threads/([^/]+)", self.path):
                thread = STATE.get_thread(match.group(1))
                if thread is None:
                    self._send(HTTPStatus.NOT_FOUND, {"error": "thread_not_found"})
                else:
                    self._send(HTTPStatus.OK, thread)
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
                text = value.get("text")
                if not isinstance(text, str) or not text.strip():
                    self._send(
                        HTTPStatus.BAD_REQUEST,
                        {"error": "bad_request", "message": "text must be a non-empty string"},
                    )
                    return
                classification = Classification(
                    str(value.get("classification", Classification.DEVELOPMENT.value))
                )
                status, response = STATE.add_turn(
                    match.group(1), text.strip(), classification
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
