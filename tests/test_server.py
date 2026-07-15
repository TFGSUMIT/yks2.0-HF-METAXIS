import json
import threading
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

from metaxis.contracts import BrainProvenance, BrainResponse
from metaxis.policy import Classification
from metaxis.server import RuntimeState, _yeti_live_brief, make_server
from metaxis.storage import MemoryStateStore


class RecordingAdapter:
    adapter_id = "recording-development"

    def __init__(self) -> None:
        self.requests = []

    def generate(self, request):
        self.requests.append(request)
        marker = "METAXIS_CONTROL_PLANE_SNAPSHOT_JSON="
        line = next(
            value
            for value in str(request.messages[0]["content"]).splitlines()
            if value.startswith(marker)
        )
        snapshot = json.loads(line.removeprefix(marker))
        draft = json.dumps(
            {
                "schema": "metaxis-draft/v1",
                "answer": "recorded",
                "claims": [
                    {
                        "fact": key,
                        "value": value,
                        "source": "metaxis-control-plane",
                    }
                    for key, value in snapshot["facts"].items()
                ],
                "proposed_actions": [],
                "non_claims": [],
            }
        )
        return BrainResponse(
            request_id=request.request_id,
            text=draft,
            provenance=BrainProvenance(
                provider="test",
                model_repository="test/model",
                model_revision="revision",
                runtime="test-runtime",
                runtime_version="1",
                route=self.adapter_id,
            ),
        )


class LocalServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = make_server(port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, path: str, value: dict | None = None):
        data = None if value is None else json.dumps(value).encode()
        request = urllib.request.Request(
            self.base + path,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        return urllib.request.urlopen(request, timeout=2)

    def test_health(self) -> None:
        with self.request("/healthz") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.load(response)["status"], "ok")

    def test_operator_state_is_native_and_noforn_blocked(self) -> None:
        with self.request("/api/v1/operator-state") as response:
            value = json.load(response)
        self.assertEqual(value["application"]["surface"], "native-installed-app")
        self.assertFalse(value["application"]["browser_required"])
        self.assertEqual(value["classification"]["status"], "BLOCKED")
        self.assertFalse(value["model"]["external_api_allowed"])
        self.assertEqual(
            value["model"]["primary_candidate"],
            "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16",
        )
        self.assertEqual(value["storage"]["backend"], "memory-development")
        self.assertFalse(value["storage"]["durable"])
        self.assertFalse(value["storage"]["credential_exposed_to_model"])
        self.assertEqual(
            value["integrations"]["github"]["authority_repo"],
            "LittleYeti-Dev/yks2.0-ops-hub",
        )
        self.assertFalse(value["integrations"]["github"]["writes_allowed"])
        self.assertEqual(value["capabilities"]["profile"], "PROTOS-4")
        self.assertEqual(value["capabilities"]["loaded_count"], 4)
        self.assertEqual(value["capabilities"]["active_count"], 2)
        self.assertFalse(value["capabilities"]["credential_exposed_to_model"])

    def test_capability_inventory_is_read_only(self) -> None:
        with self.request("/api/v1/capabilities") as response:
            value = json.load(response)
        self.assertEqual(value["authority"]["safe_chain"], [474, 475, 476])
        self.assertEqual(value["skills"][0]["id"], "yeti-boot")
        self.assertTrue(all(not item["writes_allowed"] for item in value["plugins"]))

    def test_thread_flow_uses_mock_for_development(self) -> None:
        with self.request("/api/v1/threads", {"title": "proof"}) as response:
            thread = json.load(response)
        with self.request(
            f"/api/v1/threads/{thread['id']}/turns",
            {"text": "hello", "classification": "DEVELOPMENT"},
        ) as response:
            turn = json.load(response)
        self.assertEqual(turn["route"], "mock-local-development")

    def test_yetis_live_uses_deterministic_boot_route(self) -> None:
        for trigger in ("Yetis live", "Yeti’s live", "Yeti live", "Yeti's life"):
            with self.subTest(trigger=trigger):
                with self.request("/api/v1/threads", {"title": "boot"}) as response:
                    thread = json.load(response)
                with self.request(
                    f"/api/v1/threads/{thread['id']}/turns",
                    {"text": trigger, "classification": "DEVELOPMENT"},
                ) as response:
                    turn = json.load(response)
                self.assertEqual(turn["route"], "yeti-boot-local-readback")
                self.assertIn("YKS Ops Live Brief", turn["assistant"])
                self.assertIn("HIGH/NOFORN remains blocked", turn["assistant"])
                self.assertIn("No external model was called", turn["assistant"])
                self.assertIn("GitHub broker: declared-only", turn["assistant"])
                self.assertIn("Brain route: mock-local-development", turn["assistant"])
                self.assertIn("Capability pack: 2 active / 4 loaded", turn["assistant"])
                self.assertIn("D1 adapter credential: absent", turn["assistant"])

    def test_yeti_brief_reports_live_d1_credential_boundary(self) -> None:
        brief = _yeti_live_brief(
            {
                "backend": "cloudflare-d1",
                "durable": True,
                "credential_exposed_to_model": False,
            },
            {"live": True},
            "mock-local-development",
            {"active_count": 3, "loaded_count": 4},
        )
        self.assertIn("D1 adapter credential: active from a read-only file mount", brief)
        self.assertIn("exposed to the model: never", brief)
        self.assertIn("Project 21", brief)
        self.assertIn("D1 schema administration", brief)
        self.assertNotIn("does not currently hold Cloudflare credentials", brief)
        self.assertNotIn("Project 18", brief)

    def test_github_question_uses_broker_readback_not_brain(self) -> None:
        with self.request("/api/v1/threads", {"title": "github"}) as response:
            thread = json.load(response)
        with self.request(
            f"/api/v1/threads/{thread['id']}/turns",
            {"text": "what gh are you talking to", "classification": "DEVELOPMENT"},
        ) as response:
            turn = json.load(response)
        self.assertEqual(turn["route"], "github-readback-local")
        self.assertIn("LittleYeti-Dev/yks2.0-ops-hub", turn["assistant"])
        self.assertIn("Credential exposed to the model: never", turn["assistant"])

    def test_high_noforn_turn_is_denied(self) -> None:
        with self.request("/api/v1/threads", {"title": "denial"}) as response:
            thread = json.load(response)
        with self.assertRaises(urllib.error.HTTPError) as raised:
            self.request(
                f"/api/v1/threads/{thread['id']}/turns",
                {"text": "protected", "classification": "HIGH/NOFORN"},
            )
        self.assertEqual(raised.exception.code, 403)
        value = json.load(raised.exception)
        raised.exception.close()
        self.assertEqual(value["error"], "route_blocked")

    def test_blank_or_misnamed_turn_is_rejected(self) -> None:
        with self.request("/api/v1/threads", {"title": "invalid turn"}) as response:
            thread = json.load(response)
        for payload in ({"text": "   "}, {"content": "wrong field"}):
            with self.assertRaises(urllib.error.HTTPError) as raised:
                self.request(
                    f"/api/v1/threads/{thread['id']}/turns",
                    payload,
                )
            self.assertEqual(raised.exception.code, 400)
            raised.exception.close()

    def test_thread_can_be_loaded_by_id(self) -> None:
        with self.request("/api/v1/threads", {"title": "resume me"}) as response:
            thread = json.load(response)
        with self.request(f"/api/v1/threads/{thread['id']}") as response:
            loaded = json.load(response)
        self.assertEqual(loaded["title"], "resume me")


class ConversationContextTests(unittest.TestCase):
    def test_prior_turns_are_bounded_and_sent_as_model_context(self) -> None:
        state = RuntimeState(store=MemoryStateStore())
        adapter = RecordingAdapter()
        state._adapter = adapter
        thread = state.create_thread("context")
        with patch.dict(
            "os.environ",
            {"METAXIS_BRAIN_CONTEXT_TURNS": "1", "METAXIS_BRAIN_CONTEXT_CHARS": "24000"},
            clear=False,
        ):
            state.add_turn(thread["id"], "first", Classification.DEVELOPMENT)
            state.add_turn(thread["id"], "second", Classification.DEVELOPMENT)
        messages = adapter.requests[-1].messages
        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("Active brain route: recording-development", messages[0]["content"])
        self.assertIn("This answer uses external inference: true", messages[0]["content"])
        self.assertIn("does not make D1 itself read-only", messages[0]["content"])
        self.assertEqual(messages[-3:], (
            {"role": "user", "content": "first"},
            {"role": "assistant", "content": state.get_thread(thread["id"])["turns"][0]["assistant"]},
            {"role": "user", "content": "second"},
        ))

    def test_invalid_external_draft_is_repaired_once(self) -> None:
        class RepairingAdapter(RecordingAdapter):
            def __init__(self):
                super().__init__()
                self.calls = 0

            def generate(self, request):
                self.calls += 1
                if self.calls == 1:
                    self.requests.append(request)
                    return BrainResponse(
                        request_id=request.request_id,
                        text="not json",
                        provenance=BrainProvenance(
                            provider="test",
                            model_repository="test/model",
                            model_revision="revision",
                            runtime="test-runtime",
                            runtime_version="1",
                            route=self.adapter_id,
                        ),
                    )
                return super().generate(request)

        state = RuntimeState(store=MemoryStateStore())
        adapter = RepairingAdapter()
        state._adapter = adapter
        thread = state.create_thread("repair")
        status, turn = state.add_turn(
            thread["id"], "repair this", Classification.DEVELOPMENT
        )
        self.assertEqual(status, 201)
        self.assertEqual(turn["verification"]["status"], "VERIFIED")
        self.assertEqual(turn["verification"]["attempts"], 2)
        self.assertTrue(turn["assistant"].startswith("VERIFIED"))
        self.assertIn("METAXIS rejected", adapter.requests[-1].messages[-1]["content"])

    def test_repair_exhaustion_fails_closed_and_persists_block(self) -> None:
        class InvalidAdapter(RecordingAdapter):
            def generate(self, request):
                self.requests.append(request)
                return BrainResponse(
                    request_id=request.request_id,
                    text="not json",
                    provenance=BrainProvenance(
                        provider="test",
                        model_repository="test/model",
                        model_revision="revision",
                        runtime="test-runtime",
                        runtime_version="1",
                        route=self.adapter_id,
                    ),
                )

        state = RuntimeState(store=MemoryStateStore())
        adapter = InvalidAdapter()
        state._adapter = adapter
        thread = state.create_thread("blocked")
        status, turn = state.add_turn(
            thread["id"], "invent something", Classification.DEVELOPMENT
        )
        self.assertEqual(status, 201)
        self.assertEqual(turn["verification"]["status"], "BLOCKED")
        self.assertTrue(turn["assistant"].startswith("BLOCKED"))
        self.assertEqual(len(adapter.requests), 2)
        self.assertEqual(
            state.get_thread(thread["id"])["turns"][0]["verification"]["status"],
            "BLOCKED",
        )


if __name__ == "__main__":
    unittest.main()
