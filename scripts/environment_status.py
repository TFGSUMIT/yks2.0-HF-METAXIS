"""Print a redacted readback of the METAXIS process environment."""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Mapping


DEFAULT_SOURCE_REPO = "LittleYeti-Dev/yks2.0-ops-hub"
DEFAULT_SOURCE_ISSUE = "422"
DEFAULT_TARGET_ISSUE = "1"
RECOMMENDED_PYTHONPATH = "src:."


def build_environment_status(environ: Mapping[str, str]) -> dict[str, object]:
    credential_variable = next(
        (name for name in ("GH_TOKEN", "GITHUB_TOKEN") if environ.get(name)),
        None,
    )
    target_repo_source = None
    target_repo = environ.get("METAXIS_TARGET_REPO")
    if target_repo:
        target_repo_source = "METAXIS_TARGET_REPO"
    else:
        target_repo = environ.get("GITHUB_REPOSITORY")
        if target_repo:
            target_repo_source = "GITHUB_REPOSITORY"

    return {
        "credential": {
            "accepted_variables": ["GH_TOKEN", "GITHUB_TOKEN"],
            "configured": credential_variable is not None,
            "selected_variable": credential_variable,
        },
        "github_repository": environ.get("GITHUB_REPOSITORY"),
        "github_broker": {
            "account": environ.get("METAXIS_GITHUB_ACCOUNT", "LittleYeti-Dev"),
            "api_base": environ.get("METAXIS_GITHUB_API_BASE", "https://api.github.com"),
            "token_file_configured": bool(environ.get("METAXIS_GITHUB_TOKEN_FILE")),
            "mode": "metadata-read-only",
            "writes_allowed": False,
        },
        "huggingface": {
            "disable_implicit_token": environ.get(
                "HF_HUB_DISABLE_IMPLICIT_TOKEN", "1"
            ),
            "disable_telemetry": environ.get(
                "HF_HUB_DISABLE_TELEMETRY", "1"
            ),
            "disable_update_check": environ.get(
                "HF_HUB_DISABLE_UPDATE_CHECK", "1"
            ),
            "home": environ.get("HF_HOME", "~/.cache/huggingface"),
            "hub_cache": environ.get("HF_HUB_CACHE", "$HF_HOME/hub"),
            "offline": environ.get("HF_HUB_OFFLINE", "0"),
            "env_token_configured": bool(environ.get("HF_TOKEN")),
            "token_path_configured": bool(environ.get("HF_TOKEN_PATH")),
        },
        "state_store": {
            "backend": environ.get("METAXIS_STATE_BACKEND", "memory"),
            "cloudflare_account_configured": bool(
                environ.get("CLOUDFLARE_ACCOUNT_ID")
            ),
            "d1_database_configured": bool(
                environ.get("METAXIS_D1_DATABASE_ID")
            ),
            "d1_token_configured": bool(
                environ.get("CLOUDFLARE_D1_API_TOKEN")
                or environ.get("CLOUDFLARE_D1_API_TOKEN_FILE")
            ),
            "d1_token_file_configured": bool(
                environ.get("CLOUDFLARE_D1_API_TOKEN_FILE")
            ),
        },
        "brain": {
            "mode": environ.get("METAXIS_BRAIN_MODE", "mock"),
            "external_calls_enabled": environ.get("METAXIS_EXTERNAL_MODEL_CALLS")
            == "1",
            "endpoint_configured": bool(environ.get("METAXIS_BRAIN_URL")),
            "api_key_configured": bool(
                environ.get("METAXIS_BRAIN_API_KEY")
                or environ.get("METAXIS_BRAIN_API_KEY_FILE")
            ),
            "api_key_file_configured": bool(
                environ.get("METAXIS_BRAIN_API_KEY_FILE")
            ),
            "aws_region": environ.get("METAXIS_AWS_REGION", "us-east-1"),
            "bedrock_model_id": environ.get(
                "METAXIS_BEDROCK_MODEL_ID", "nvidia.nemotron-super-3-120b"
            ),
            "aws_credentials_file_configured": bool(
                environ.get("METAXIS_AWS_CREDENTIALS_FILE")
            ),
            "max_request_cost_usd": environ.get(
                "METAXIS_BRAIN_MAX_REQUEST_COST_USD", "0.01"
            ),
            "candidate": environ.get(
                "METAXIS_BRAIN_MODEL",
                "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16",
            ),
            "revision": environ.get(
                "METAXIS_BRAIN_REVISION",
                "d51eab0d1f979ebc26b546e634a04f450d99158e",
            ),
        },
        "pythonpath": {
            "configured": bool(environ.get("PYTHONPATH")),
            "effective": environ.get("PYTHONPATH", RECOMMENDED_PYTHONPATH),
        },
        "source_issue": environ.get(
            "METAXIS_SOURCE_ISSUE", DEFAULT_SOURCE_ISSUE
        ),
        "source_repo": environ.get("METAXIS_SOURCE_REPO", DEFAULT_SOURCE_REPO),
        "sync_ready": credential_variable is not None and bool(target_repo),
        "target_issue": environ.get(
            "METAXIS_TARGET_ISSUE", DEFAULT_TARGET_ISSUE
        ),
        "target_repo": target_repo,
        "target_repo_source": target_repo_source,
        "virtual_env_active": bool(environ.get("VIRTUAL_ENV"))
        or sys.prefix != sys.base_prefix,
    }


def main() -> int:
    print(json.dumps(build_environment_status(os.environ), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
