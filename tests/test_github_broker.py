import io
import json
import tempfile
import unittest
import urllib.request
from pathlib import Path

from metaxis.github_broker import GitHubReadBroker
from metaxis.secret_file import read_secret_file


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()


class GitHubReadBrokerTests(unittest.TestCase):
    def test_missing_credential_never_calls_network(self) -> None:
        calls = []
        broker = GitHubReadBroker(
            account="LittleYeti-Dev",
            authority_repo="LittleYeti-Dev/yks2.0-ops-hub",
            implementation_repo="LittleYeti-Dev/yks2.0-HF-METAXIS",
            opener=lambda *args, **kwargs: calls.append((args, kwargs)),
        )
        status = broker.status()
        self.assertFalse(status["live"])
        self.assertFalse(status["credential_configured"])
        self.assertFalse(status["credential_exposed_to_model"])
        self.assertFalse(status["writes_allowed"])
        self.assertEqual(calls, [])

    def test_live_read_returns_only_bounded_metadata(self) -> None:
        requests: list[urllib.request.Request] = []

        def opener(request, timeout):
            requests.append(request)
            if request.full_url.endswith("/user"):
                value = {"login": "LittleYeti-Dev", "email": "do-not-return"}
            else:
                full_name = request.full_url.split("/repos/", 1)[1]
                value = {
                    "full_name": full_name,
                    "private": True,
                    "visibility": "private",
                    "default_branch": "main",
                    "archived": False,
                    "updated_at": "2026-07-14T00:00:00Z",
                    "permissions": {"admin": True},
                }
            return _Response(json.dumps(value).encode())

        broker = GitHubReadBroker(
            account="configured-account",
            authority_repo="LittleYeti-Dev/yks2.0-ops-hub",
            implementation_repo="LittleYeti-Dev/yks2.0-HF-METAXIS",
            token="test-secret",
            opener=opener,
        )
        status = broker.status()
        self.assertTrue(status["live"])
        self.assertEqual(status["account"], "LittleYeti-Dev")
        self.assertEqual(len(status["repositories"]), 2)
        self.assertNotIn("permissions", status["repositories"][0])
        self.assertNotIn("email", status)
        self.assertTrue(
            all(request.get_header("Authorization") == "Bearer test-secret" for request in requests)
        )

    def test_token_file_requires_absolute_regular_nonempty_file(self) -> None:
        with self.assertRaises(ValueError):
            read_secret_file("relative-token", "METAXIS_GITHUB_TOKEN_FILE")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "token"
            path.write_text("test-secret\n", encoding="utf-8")
            path.chmod(0o600)
            self.assertEqual(
                read_secret_file(str(path), "METAXIS_GITHUB_TOKEN_FILE"),
                "test-secret",
            )
            path.chmod(0o644)
            with self.assertRaises(ValueError):
                read_secret_file(str(path), "METAXIS_GITHUB_TOKEN_FILE")

    def test_repository_coordinates_reject_path_injection(self) -> None:
        with self.assertRaises(ValueError):
            GitHubReadBroker(
                account="LittleYeti-Dev",
                authority_repo="LittleYeti-Dev/../settings",
                implementation_repo="LittleYeti-Dev/yks2.0-HF-METAXIS",
            )
