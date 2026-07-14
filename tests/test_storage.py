import json
import os
import unittest
from unittest.mock import patch

from metaxis.storage import (
    CloudflareD1StateStore,
    D1Settings,
    MemoryStateStore,
    StorageConfigurationError,
    StorageUnavailableError,
    state_store_from_environment,
)


class MemoryStateStoreTests(unittest.TestCase):
    def test_thread_and_turn_are_reconstructed_without_aliasing(self) -> None:
        store = MemoryStateStore()
        thread = store.create_thread(" proof ")
        turn = {
            "id": "turn-1",
            "created_at": "2026-07-14T00:00:00+00:00",
            "classification": "DEVELOPMENT",
            "operator": "hello",
            "assistant": "ready",
            "route": "mock-local-development",
        }
        store.append_turn(thread["id"], turn)

        listed = store.list_threads()
        self.assertEqual(listed[0]["title"], "proof")
        self.assertEqual(listed[0]["turns"], [turn])
        listed[0]["turns"].clear()
        self.assertEqual(len(store.list_threads()[0]["turns"]), 1)


class CloudflareD1StateStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.requests = []

    def transport(self, request, timeout):
        self.requests.append((request, timeout))
        body = json.loads(request.data)
        statements = body.get("batch", [body])
        return {
            "success": True,
            "result": [
                {"success": True, "results": [], "meta": {}}
                for _ in statements
            ],
        }

    def store(self, transport=None) -> CloudflareD1StateStore:
        return CloudflareD1StateStore(
            D1Settings("account", "database", "secret-token"),
            transport or self.transport,
        )

    def test_create_uses_batch_parameter_binding_and_bearer_auth(self) -> None:
        thread = self.store().create_thread("D1 proof")
        request, timeout = self.requests[0]
        body = json.loads(request.data)

        self.assertEqual(thread["title"], "D1 proof")
        self.assertEqual(timeout, 10.0)
        self.assertEqual(len(body["batch"]), 2)
        self.assertIn("?1", body["batch"][0]["sql"])
        self.assertEqual(body["batch"][0]["params"][1], "D1 proof")
        self.assertEqual(request.get_header("Authorization"), "Bearer secret-token")
        self.assertNotIn("secret-token", request.data.decode())

    def test_list_reconstructs_thread_and_turn_with_one_query(self) -> None:
        def transport(request, timeout):
            self.requests.append((request, timeout))
            return {
                "success": True,
                "result": [
                    {
                        "success": True,
                        "results": [
                            {
                                "thread_id": "thread-1",
                                "thread_title": "proof",
                                "thread_created_at": "t0",
                                "turn_id": "turn-1",
                                "turn_created_at": "t1",
                                "turn_classification": "DEVELOPMENT",
                                "operator_text": "hello",
                                "assistant_text": "ready",
                                "route": "mock-local-development",
                            }
                        ],
                    }
                ],
            }

        threads = self.store(transport).list_threads()
        self.assertEqual(len(self.requests), 1)
        self.assertEqual(threads[0]["turns"][0]["assistant"], "ready")

    def test_rejected_query_fails_closed_without_echoing_secret(self) -> None:
        def rejected(request, timeout):
            return {"success": False, "errors": [{"message": "denied"}]}

        with self.assertRaises(StorageUnavailableError) as raised:
            self.store(rejected).list_threads()
        self.assertNotIn("secret-token", str(raised.exception))


class StateStoreEnvironmentTests(unittest.TestCase):
    def test_default_is_memory(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsInstance(state_store_from_environment(), MemoryStateStore)

    def test_explicit_d1_missing_credentials_fails_closed(self) -> None:
        with patch.dict(
            os.environ, {"METAXIS_STATE_BACKEND": "cloudflare-d1"}, clear=True
        ):
            with self.assertRaises(StorageConfigurationError):
                state_store_from_environment()


if __name__ == "__main__":
    unittest.main()
