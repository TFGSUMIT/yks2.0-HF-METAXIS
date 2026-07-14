import unittest

from metaxis.adapters import APIBackendConfig, OpenAICompatibleAdapter
from metaxis.contracts import BrainRequest
from metaxis.policy import DEVELOPMENT_ROUTE


class APIAdapterTests(unittest.TestCase):
    def test_high_noforn_is_denied_before_network(self) -> None:
        adapter = OpenAICompatibleAdapter(
            APIBackendConfig(
                endpoint="http://127.0.0.1:1",
                api_key="not-used",
                route=DEVELOPMENT_ROUTE,
            )
        )
        response = adapter.generate(
            BrainRequest(
                request_id="denial-proof",
                messages=({"role": "user", "content": "protected"},),
                authority_context={"classification": "HIGH/NOFORN"},
            )
        )
        self.assertIsNotNone(response.error)
        self.assertEqual(response.error.code, "route_blocked")

    def test_token_ceiling_denies_before_network(self) -> None:
        adapter = OpenAICompatibleAdapter(
            APIBackendConfig(
                endpoint="http://127.0.0.1:1",
                api_key="not-used",
                route=DEVELOPMENT_ROUTE,
                max_output_tokens=10,
            )
        )
        response = adapter.generate(
            BrainRequest(
                request_id="quota-proof",
                messages=({"role": "user", "content": "public"},),
                max_output_tokens=11,
                authority_context={"classification": "DEVELOPMENT"},
            )
        )
        self.assertIsNotNone(response.error)
        self.assertEqual(response.error.code, "quota_exceeded")


if __name__ == "__main__":
    unittest.main()
