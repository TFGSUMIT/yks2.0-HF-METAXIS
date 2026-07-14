import json
import threading
import unittest
import urllib.error
import urllib.request

from metaxis.server import make_server


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
        self.assertEqual(value["storage"]["backend"], "memory-development")
        self.assertFalse(value["storage"]["durable"])
        self.assertFalse(value["storage"]["credential_exposed_to_model"])

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


if __name__ == "__main__":
    unittest.main()
