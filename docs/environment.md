# METAXIS Environment Contract

Status: Phase 0 development contract  
Authority: YKS Ops issues 422 and 423

METAXIS keeps configuration names and non-secret defaults in the repository.
Credentials remain in an external secret authority or an authorized CI secret
store. Never commit a populated `.env` file.

## Variables

| Variable | Required | Secret | Default / source | Purpose |
| --- | --- | --- | --- | --- |
| `GH_TOKEN` | For live issue sync | Yes | None | Preferred GitHub credential for reading the private YKS Ops authority and updating the METAXIS mirror. |
| `GITHUB_TOKEN` | Fallback for live issue sync | Yes | GitHub Actions may supply it | Credential fallback when `GH_TOKEN` is unset. The built-in Actions token cannot read the private authority repository, so the mirror workflow maps `YKS_OPS_SYNC_TOKEN` into `GH_TOKEN`. |
| `METAXIS_SOURCE_REPO` | No | No | `LittleYeti-Dev/yks2.0-ops-hub` | Authoritative YKS Ops repository. |
| `METAXIS_SOURCE_ISSUE` | No | No | `422` | Authoritative METAXIS root issue. |
| `METAXIS_TARGET_REPO` | Yes for local sync | No | Falls back to `GITHUB_REPOSITORY` | METAXIS implementation repository containing the read-only mirror. |
| `METAXIS_TARGET_ISSUE` | No | No | `1` | Read-only mirror issue number. |
| `GITHUB_REPOSITORY` | GitHub Actions context only | No | Supplied by GitHub Actions | Target-repository fallback used when `METAXIS_TARGET_REPO` is unset. |
| `PYTHONPATH` | No | No | Recommended `src:.` for direct checkout execution | Makes the source package importable when it has not been installed into the active Python environment. |
| `VIRTUAL_ENV` | No | No | Set by Python environment activation | Indicates that the managed `.venv` is active. It is inspected only by the safe environment-status readback. |
| `HF_TOKEN` | For authorized private/gated or write operations | Yes | L2 credential mesh injection | Hugging Face user access token. Connector authentication is separate and does not populate this variable. |
| `HF_HUB_DISABLE_IMPLICIT_TOKEN` | No | No | METAXIS default `1` | Prevents automatic token attachment to public read requests. Authorized calls must request authentication explicitly. |
| `HF_HUB_DISABLE_TELEMETRY` | No | No | METAXIS default `1` | Disables Hugging Face library telemetry for the governed research environment. |
| `HF_HUB_DISABLE_UPDATE_CHECK` | No | No | METAXIS default `1` | Prevents unpinned CLI update checks during repeatable runs. |
| `HF_HUB_OFFLINE` | No | No | METAXIS default `0` | Enables explicit offline mode when set to `1`; Phase 0 Hub discovery requires online mode. |
| `HF_HOME` | No | No | `~/.cache/huggingface` | Optional external root for Hugging Face cache and token state; never point it inside the repository. |
| `HF_HUB_CACHE` | No | No | `$HF_HOME/hub` | Optional external model/dataset cache location. |
| `HF_TOKEN_PATH` | No | Yes-bearing path | `$HF_HOME/token` | Optional token-file path. METAXIS prefers L2 environment injection rather than a persistent token file. |

The GitHub Actions secret `YKS_OPS_SYNC_TOKEN` is repository configuration,
not a process variable consumed by Python. The workflow exposes it to the
process as `GH_TOKEN`. Its value must never appear in logs or repository files.

## L2 Credential Mesh Binding

YKS Ops issue 422 authorizes the METAXIS root mirror. The workflow credential
is treated as an L2 DevSecOps credential and is held by the GitHub Actions
secret store as `YKS_OPS_SYNC_TOKEN`; the workflow releases it only to the
mirror step as `GH_TOKEN`.

Current non-secret functional proof:

- the secret exists in `LittleYeti-Dev/yks2.0-HF-METAXIS`;
- workflow run `29345885497` completed successfully on 2026-07-14;
- METAXIS issue 1 matched the YKS Ops issue 422 payload after the run.

Proof posture is functional but bounded. This confirms secret injection and
cross-repository mirror behavior. It does not prove least-privilege token
scope, rotation, revocation, issuer provenance, or a general-purpose L2
credential service. Those properties require YKS Ops/CUSTODIA readback before
promotion beyond this single workflow.

The Hugging Face automation token is a separate L2 credential. The authenticated
plugin connector may perform governed discovery without exporting its
credential to the worktree. The interactive CLI may use its official OAuth
session; automation uses `HF_TOKEN` only when an authorized operation requires
it. See `docs/huggingface-setup.md`.

## Local Setup

The Codex environment creates `.venv`, installs METAXIS in editable mode, runs
the tests, and prints a redacted environment status. For direct checkout use:

```text
python3 -m venv .venv
.venv/bin/python -m pip install --editable .
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/environment_status.py
```

Copy `.env.example` to `.env` only if the calling tool loads dotenv files.
Python does not load `.env` automatically, and this repository intentionally
adds no dotenv dependency in Phase 0.

## Safe Readback

Run `python3 scripts/environment_status.py`. The command reports effective
non-secret coordinates and whether credentials are configured. It never prints
credential values. `sync_ready` means only that required process inputs are
present; it does not prove authorization, connectivity, or a successful sync.
