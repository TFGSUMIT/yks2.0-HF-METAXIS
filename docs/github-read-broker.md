# GitHub read broker

Status: Phase 0 bounded implementation
Authority: YKS Ops #474 → #475 → #476

NemaShells does not receive a GitHub credential or call GitHub directly.
METAXIS owns a local, fail-closed broker that can expose only bounded account
and repository metadata for the authoritative YKS Ops repository and the
METAXIS implementation repository.

## Default readback

Without a credential, the broker reports:

- account `LittleYeti-Dev`;
- authority repository `LittleYeti-Dev/yks2.0-ops-hub`;
- implementation repository `LittleYeti-Dev/yks2.0-HF-METAXIS`;
- connection `declared-only`;
- writes denied; and
- credential exposure to the model `false`.

No unauthenticated network fallback is attempted when a private-repository
credential is absent or invalid.

## Live metadata gate

Live readback requires a fine-grained GitHub token selected only for the two
repositories above with repository Metadata read permission. Store the value
in an absolute host file outside the repository, mode `0600`, then set:

```text
METAXIS_GITHUB_TOKEN_FILE=/absolute/external/path/github-read-token
```

The OrbStack installer mounts the file read-only at
`/run/secrets/metaxis_github_token`. The broker reads it at startup, sends it
only in the GitHub REST authorization header, caches a bounded read for 60
seconds, and never returns the credential, email, raw permissions, or response
body to the UI or brain.

The current live contract reads `/user` and `GET /repos/{owner}/{repo}`. It
returns login, repository name, private/visibility posture, default branch,
archive state, and update time. GitHub issue, project, workflow, content, and
write operations are not part of this slice.

## Failure behavior

- A configured missing, relative, oversized, empty, or group/world-readable
  token file fails startup.
- A GitHub HTTP, timeout, or payload failure returns `live-read-failed` without
  exposing the provider response body.
- The broker never falls through to `GH_TOKEN` or `GITHUB_TOKEN`.
- The model receives only the normalized readback, never the credential.

This is functional metadata integration, not GitHub execution authority.
Write operations require a separate contract, separate credential, explicit
operator approval, evidence, and recovery behavior.
