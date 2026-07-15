from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "assets" / "brand"


class SkipJackConsoleDesignLanguageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads((BRAND / "artifact-manifest.json").read_text())
        self.artifacts = {
            item["artifact_id"]: item for item in self.manifest["artifacts"]
        }

    def test_design_language_is_current_and_prior_ui_artifacts_are_superseded(self) -> None:
        design = self.artifacts["MTX-ART-DL-20260715-004"]
        self.assertEqual(design["status"], "accepted-current")
        self.assertEqual(
            design["source_design_language"], "SKIPJACK-CONSOLE-DL-1.0"
        )
        self.assertEqual(
            design["live_d1_receipt"], "MTX-DESIGN-OUTPUT-SJCDL-20260715-001"
        )
        for artifact_id in (
            "MTX-ART-UI-20260714-002",
            "MTX-ART-UI-20260714-003",
        ):
            self.assertEqual(self.artifacts[artifact_id]["status"], "superseded")

    def test_reference_images_exist_and_match_manifest_hashes(self) -> None:
        for artifact_id in (
            "MTX-ART-UI-20260715-005",
            "MTX-ART-UI-20260715-006",
        ):
            artifact = self.artifacts[artifact_id]
            path = ROOT / artifact["files"][0]
            self.assertTrue(path.is_file())
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest, artifact["png_sha256"])

    def test_source_spec_carries_required_ui_contract(self) -> None:
        source = (BRAND / "skipjack-console-design-language-v1.0.md").read_text()
        for token in (
            "SKIPJACK-CONSOLE-DL-1.0",
            "MTX-ART-DL-20260715-004",
            "Standard Clean",
            "Standard Unpacked",
            "Complex Unpacked",
            "Ten is the hard maximum",
            "NemaShells is not visible branding",
            "Message METAXIS",
            "Future Capability: Multi-Monitor Workspace",
            "ten-card hard maximum applies across the complete",
            "single-monitor fallback",
        ):
            self.assertIn(token, source)

        design = self.artifacts["MTX-ART-DL-20260715-004"]
        capability = design["future_capabilities"][0]
        self.assertEqual(capability["capability"], "multi-monitor-workspace")
        self.assertEqual(capability["state"], "planned-deferred")
        self.assertEqual(capability["scope"], "every METAXIS UI")


if __name__ == "__main__":
    unittest.main()
