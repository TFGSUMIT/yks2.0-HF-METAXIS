import json
import threading
import unittest
import urllib.error
import urllib.request

from metaxis.lector import (
    ContextRequest,
    InMemoryLector,
    RetrievalAuthority,
    SourceChunk,
    SourceRecord,
)
from metaxis.lector.server import make_server


def source(source_id: str) -> SourceRecord:
    return SourceRecord(
        source_id=source_id,
        canonical_uri=f"https://example.test/{source_id}",
        version="v1",
        content_hash=f"sha256:{source_id}",
        license_ref="Apache-2.0",
        classification="PUBLIC",
        allowed_use="development",
        owner="test-owner",
        freshness_at="2026-07-15T00:00:00Z",
    )


class LectorContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.allowed = SourceChunk(
            source=source("allowed"),
            chunk_id="chunk-a",
            content="LECTOR delivers governed retrieval context with citations.",
            citation="allowed#chunk-a",
        )
        self.denied = SourceChunk(
            source=source("denied"),
            chunk_id="chunk-b",
            content="LECTOR must not leak denied source content.",
            citation="denied#chunk-b",
        )

    def request(self, **overrides):
        values = {
            "request_id": "request-1",
            "query": "governed retrieval citations",
            "authority": RetrievalAuthority("axis-decision-1", frozenset({"allowed"})),
            "max_results": 5,
            "context_budget_chars": 1000,
        }
        values.update(overrides)
        return ContextRequest(**values)

    def test_source_metadata_is_required(self) -> None:
        with self.assertRaises(ValueError):
            SourceRecord(
                source_id="",
                canonical_uri="https://example.test/source",
                version="v1",
                content_hash="sha256:source",
                license_ref="Apache-2.0",
                classification="PUBLIC",
                allowed_use="development",
                owner="test-owner",
                freshness_at="2026-07-15T00:00:00Z",
            )

    def test_retrieval_fails_closed_when_no_registered_source_is_eligible(self) -> None:
        response = InMemoryLector((self.denied,)).retrieve(self.request())
        self.assertEqual(response.status, "denied")
        self.assertEqual(response.items, ())
        self.assertIn("no registered source is eligible", response.denials[0])

    def test_retrieval_returns_provenance_only_for_allowed_sources(self) -> None:
        response = InMemoryLector((self.denied, self.allowed)).retrieve(self.request())
        self.assertEqual(response.status, "delivered")
        self.assertEqual(len(response.items), 1)
        item = response.items[0]
        self.assertEqual(item.source_id, "allowed")
        self.assertEqual(item.source_version, "v1")
        self.assertEqual(item.content_hash, "sha256:allowed")
        self.assertEqual(item.citation, "allowed#chunk-a")

    def test_context_budget_denial_is_visible(self) -> None:
        response = InMemoryLector((self.allowed,)).retrieve(
            self.request(context_budget_chars=4)
        )
        self.assertEqual(response.status, "denied")
        self.assertIn("context budget", response.denials[0])


class LectorServerTests(unittest.TestCase):
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
        return urllib.request.urlopen(
            urllib.request.Request(
                self.base + path,
                data=data,
                headers={"Content-Type": "application/json"},
            ),
            timeout=2,
        )

    def test_health_declares_no_operator_or_tool_surface(self) -> None:
        with self.request("/healthz") as response:
            value = json.load(response)
        self.assertEqual(value["service"], "lector")
        self.assertEqual(value["operator_routes"], "denied")
        self.assertEqual(value["tool_execution"], "denied")

    def test_context_requires_explicit_eligibility(self) -> None:
        with self.assertRaises(urllib.error.HTTPError) as raised:
            self.request("/api/v1/context", {"request_id": "request-1", "query": "test"})
        self.assertEqual(raised.exception.code, 400)
        raised.exception.close()

    def test_no_tool_route_exists(self) -> None:
        with self.assertRaises(urllib.error.HTTPError) as raised:
            self.request("/api/v1/tools", {})
        self.assertEqual(raised.exception.code, 404)
        raised.exception.close()


if __name__ == "__main__":
    unittest.main()
