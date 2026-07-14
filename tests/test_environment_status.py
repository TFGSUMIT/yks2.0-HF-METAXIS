import io
import os
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from scripts.environment_status import build_environment_status, main


class EnvironmentStatusTests(unittest.TestCase):
    def test_defaults_are_honest_about_missing_live_sync_inputs(self) -> None:
        status = build_environment_status({})

        self.assertEqual(status["source_issue"], "422")
        self.assertEqual(status["target_issue"], "1")
        self.assertIsNone(status["target_repo"])
        self.assertFalse(status["sync_ready"])
        self.assertFalse(status["huggingface"]["env_token_configured"])
        self.assertEqual(status["huggingface"]["disable_implicit_token"], "1")
        self.assertFalse(status["github_broker"]["token_file_configured"])
        self.assertFalse(status["github_broker"]["writes_allowed"])
        self.assertEqual(status["brain"]["mode"], "mock")
        self.assertFalse(status["brain"]["external_calls_enabled"])
        self.assertFalse(status["brain"]["aws_credentials_file_configured"])
        self.assertEqual(status["brain"]["max_request_cost_usd"], "0.01")
        self.assertEqual(
            status["brain"]["candidate"],
            "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16",
        )
        self.assertEqual(
            status["brain"]["revision"],
            "d51eab0d1f979ebc26b546e634a04f450d99158e",
        )

    def test_secret_value_is_never_returned_or_printed(self) -> None:
        secret = "never-print-this-token"
        environ = {
            "GH_TOKEN": secret,
            "HF_TOKEN": secret,
            "CLOUDFLARE_D1_API_TOKEN": secret,
            "METAXIS_BRAIN_API_KEY_FILE": f"/tmp/{secret}-brain",
            "METAXIS_GITHUB_TOKEN_FILE": f"/tmp/{secret}",
            "METAXIS_STATE_BACKEND": "cloudflare-d1",
            "METAXIS_TARGET_REPO": "LittleYeti-Dev/yks2.0-HF-METAXIS",
        }

        status = build_environment_status(environ)
        self.assertTrue(status["credential"]["configured"])
        self.assertEqual(status["credential"]["selected_variable"], "GH_TOKEN")
        self.assertNotIn(secret, repr(status))

        output = io.StringIO()
        with patch.dict(os.environ, environ, clear=True), redirect_stdout(output):
            self.assertEqual(main(), 0)
        self.assertNotIn(secret, output.getvalue())
        self.assertTrue(status["state_store"]["d1_token_configured"])
        self.assertTrue(status["github_broker"]["token_file_configured"])
        self.assertTrue(status["brain"]["api_key_configured"])
        self.assertNotIn(secret, repr(status))


if __name__ == "__main__":
    unittest.main()
