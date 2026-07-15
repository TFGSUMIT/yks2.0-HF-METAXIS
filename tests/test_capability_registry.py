import unittest

from metaxis.capability_registry import (
    CapabilityManifestError,
    CapabilityRegistry,
    REGISTRY,
)


class CapabilityRegistryTests(unittest.TestCase):
    def test_protos_4_pack_is_pinned_and_fail_closed(self) -> None:
        status = REGISTRY.status()
        self.assertEqual(status["profile"], "PROTOS-4")
        self.assertEqual(status["loaded_count"], 4)
        self.assertEqual(status["active_count"], 2)
        self.assertFalse(status["credential_exposed_to_model"])
        self.assertEqual(status["authority"]["safe_chain"], [474, 475, 476])
        self.assertTrue(all(not item["writes_allowed"] for item in status["plugins"]))

    def test_manifest_rejects_write_grant(self) -> None:
        manifest = REGISTRY.status()
        manifest["schema_version"] = 1
        manifest["plugins"][0]["writes_allowed"] = True
        with self.assertRaises(CapabilityManifestError):
            CapabilityRegistry(manifest)

    def test_runtime_gate_can_activate_loaded_adapter_without_write_grant(self) -> None:
        status = REGISTRY.status(activated_ids={"cloudflare"})
        cloudflare = next(
            item for item in status["plugins"] if item["id"] == "cloudflare"
        )
        self.assertEqual(status["active_count"], 3)
        self.assertTrue(cloudflare["active"])
        self.assertFalse(cloudflare["writes_allowed"])

    def test_runtime_gate_rejects_unknown_capability(self) -> None:
        with self.assertRaises(CapabilityManifestError):
            REGISTRY.status(activated_ids={"not-loaded"})


if __name__ == "__main__":
    unittest.main()
