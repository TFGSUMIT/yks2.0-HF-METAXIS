import unittest

from scripts.sync_root_issue import build_mirror_body


class RootIssueMirrorTests(unittest.TestCase):
    def test_mirror_body_declares_one_way_authority(self) -> None:
        result = build_mirror_body(
            "LittleYeti-Dev/yks2.0-ops-hub",
            422,
            "https://github.com/LittleYeti-Dev/yks2.0-ops-hub/issues/422",
            "# Source body",
        )
        self.assertIn("One-way mirror", result)
        self.assertIn("Do not edit this copy directly", result)
        self.assertTrue(result.endswith("# Source body"))


if __name__ == "__main__":
    unittest.main()

