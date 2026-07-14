"""One-way mirror of the authoritative METAXIS root issue into this repo."""

from __future__ import annotations

import json
import os
import sys
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


API_ROOT = "https://api.github.com"
MIRROR_MARKER = "<!-- METAXIS_ROOT_MIRROR: source={source_repo}#{source_issue} -->"


def build_mirror_body(
    source_repo: str, source_issue: int, source_url: str, source_body: str
) -> str:
    marker = MIRROR_MARKER.format(
        source_repo=source_repo, source_issue=source_issue
    )
    notice = (
        "> [!IMPORTANT]\n"
        f"> **One-way mirror.** Work in [YKS Ops #{source_issue}]({source_url}); "
        "this issue is automatically synchronized from that authority. "
        "Do not edit this copy directly."
    )
    return f"{marker}\n{notice}\n\n{source_body or ''}"


class GitHubAPI:
    def __init__(self, token: str) -> None:
        if not token:
            raise ValueError("GITHUB_TOKEN is required")
        self.token = token

    def request(
        self, method: str, path: str, payload: dict[str, Any] | None = None
    ) -> Any:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            f"{API_ROOT}{path}",
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "yks-metaxis-root-mirror",
            },
        )
        with urlopen(request, timeout=30) as response:
            body = response.read()
        return None if not body else json.loads(body)

    def upsert_label(self, repo: str, label: dict[str, Any]) -> None:
        encoded = quote(label["name"], safe="")
        payload = {
            "name": label["name"],
            "color": label["color"],
            "description": label.get("description") or "",
        }
        try:
            self.request("GET", f"/repos/{repo}/labels/{encoded}")
        except HTTPError as error:
            if error.code != 404:
                raise
            self.request("POST", f"/repos/{repo}/labels", payload)
        else:
            self.request("PATCH", f"/repos/{repo}/labels/{encoded}", payload)

    def ensure_milestone(
        self, repo: str, source_milestone: dict[str, Any] | None
    ) -> int | None:
        if not source_milestone:
            return None
        milestones = self.request(
            "GET", f"/repos/{repo}/milestones?state=all&per_page=100"
        )
        for milestone in milestones:
            if milestone["title"] == source_milestone["title"]:
                return int(milestone["number"])
        created = self.request(
            "POST",
            f"/repos/{repo}/milestones",
            {
                "title": source_milestone["title"],
                "state": source_milestone.get("state", "open"),
                "description": source_milestone.get("description") or "",
                "due_on": source_milestone.get("due_on"),
            },
        )
        return int(created["number"])


def sync(
    api: GitHubAPI,
    source_repo: str,
    source_issue_number: int,
    target_repo: str,
    target_issue_number: int,
) -> dict[str, Any]:
    source = api.request(
        "GET", f"/repos/{source_repo}/issues/{source_issue_number}"
    )
    labels = source.get("labels", [])
    for label in labels:
        api.upsert_label(target_repo, label)

    milestone_number = api.ensure_milestone(target_repo, source.get("milestone"))
    payload = {
        "title": source["title"],
        "body": build_mirror_body(
            source_repo,
            source_issue_number,
            source["html_url"],
            source.get("body") or "",
        ),
        "state": source["state"],
        "labels": [label["name"] for label in labels],
        "assignees": [assignee["login"] for assignee in source.get("assignees", [])],
        "milestone": milestone_number,
    }
    target = api.request(
        "PATCH", f"/repos/{target_repo}/issues/{target_issue_number}", payload
    )
    return {
        "source": source["html_url"],
        "target": target["html_url"],
        "labels": payload["labels"],
        "milestone": milestone_number,
        "source_updated_at": source["updated_at"],
    }


def main() -> int:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    source_repo = os.environ.get(
        "METAXIS_SOURCE_REPO", "LittleYeti-Dev/yks2.0-ops-hub"
    )
    source_issue = int(os.environ.get("METAXIS_SOURCE_ISSUE", "422"))
    target_repo = os.environ.get(
        "METAXIS_TARGET_REPO", os.environ.get("GITHUB_REPOSITORY", "")
    )
    target_issue = int(os.environ.get("METAXIS_TARGET_ISSUE", "1"))
    if not target_repo:
        print("METAXIS_TARGET_REPO or GITHUB_REPOSITORY is required", file=sys.stderr)
        return 2

    result = sync(
        GitHubAPI(token), source_repo, source_issue, target_repo, target_issue
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

