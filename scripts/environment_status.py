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
