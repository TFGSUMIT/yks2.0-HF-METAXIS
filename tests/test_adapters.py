import os
import tempfile
import unittest
from unittest.mock import patch

from metaxis.adapters import (
    APIBackendConfig,
    OpenAICompatibleAdapter,
    adapter_from_environment,
)
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

    def test_external_adapter_accepts_owner_only_key_file(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as key_file:
            key_file.write("runtime-inference-key")
            key_path = key_file.name
        os.chmod(key_path, 0o600)
        try:
            environment = {
                "METAXIS_BRAIN_MODE": "openai-compatible",
                "METAXIS_EXTERNAL_MODEL_CALLS": "1",
                "METAXIS_BRAIN_URL": "https://example.invalid/v1",
                "METAXIS_BRAIN_API_KEY_FILE": key_path,
            }
            with patch.dict(os.environ, environment, clear=True):
                adapter = adapter_from_environment()
            self.assertIsInstance(adapter, OpenAICompatibleAdapter)
            self.assertEqual(adapter.config.api_key, "runtime-inference-key")
        finally:
            os.unlink(key_path)

    def test_external_adapter_rejects_accessible_key_file(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as key_file:
            key_file.write("runtime-inference-key")
            key_path = key_file.name
        os.chmod(key_path, 0o644)
        try:
            environment = {
                "METAXIS_BRAIN_MODE": "openai-compatible",
                "METAXIS_EXTERNAL_MODEL_CALLS": "1",
                "METAXIS_BRAIN_URL": "https://example.invalid/v1",
                "METAXIS_BRAIN_API_KEY_FILE": key_path,
            }
            with patch.dict(os.environ, environment, clear=True):
                with self.assertRaises(ValueError):
                    adapter_from_environment()
        finally:
            os.unlink(key_path)


if __name__ == "__main__":
    unittest.main()
