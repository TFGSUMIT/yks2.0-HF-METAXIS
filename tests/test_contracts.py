import unittest

from metaxis.contracts import BrainProvenance, BrainRequest


class BrainContractTests(unittest.TestCase):
    def test_request_requires_messages(self) -> None:
        with self.assertRaises(ValueError):
            BrainRequest(request_id="req-1", messages=[])

    def test_request_rejects_invalid_temperature(self) -> None:
        with self.assertRaises(ValueError):
            BrainRequest(
                request_id="req-1",
                messages=[{"role": "user", "content": "hello"}],
                temperature=3.0,
            )

    def test_provenance_requires_immutable_identifiers(self) -> None:
        with self.assertRaises(ValueError):
            BrainProvenance(
                provider="huggingface",
                model_repository="nvidia/example",
                model_revision="",
                runtime="vllm",
                runtime_version="0.0.0",
                route="research",
            )


if __name__ == "__main__":
    unittest.main()

