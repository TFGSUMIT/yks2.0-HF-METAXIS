from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ComponentModelTests(unittest.TestCase):
    def test_canonical_sibling_components_are_explicit(self) -> None:
        model = (ROOT / "docs" / "architecture" / "component-model.md").read_text()
        self.assertIn("EXARTYSIS — sovereign execution harness", model)
        self.assertIn("LECTOR — retrieval-augmented generation component / METAXIS RAG", model)
        self.assertIn("NemaShells — operator interface", model)
        self.assertIn("None owns or contains another", model)

    def test_external_candidates_stay_beneath_owned_contracts(self) -> None:
        model = (ROOT / "docs" / "architecture" / "component-model.md").read_text()
        self.assertIn("NVIDIA OpenShell is cataloged/deferred", model)
        self.assertIn("Accelerated Execution Plane", model)
        self.assertIn("native provider — required and sufficient", model)
        self.assertIn("YKS-REQ-MTX-EXARTYSIS-011", model)
        self.assertIn("NVIDIA RAG Blueprint, Streaming RAG, and cuVS are candidate LECTOR backends", model)
        self.assertIn("HIGH/NOFORN use", model)


if __name__ == "__main__":
    unittest.main()
