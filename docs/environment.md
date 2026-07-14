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
| `METAXIS_GITHUB_ACCOUNT` | No | No | `LittleYeti-Dev` | Declared GitHub account shown by the read-only NemaShells broker. Live identity replaces this value only after an authenticated read. |
| `METAXIS_GITHUB_API_BASE` | No | No | `https://api.github.com` | GitHub REST API base for the bounded metadata broker. |
| `METAXIS_GITHUB_TOKEN_FILE` | For live GitHub readback | Yes-bearing path | None | Absolute path to a fine-grained, repository-selected, metadata-read token file mounted read-only into METAXIS. The broker deliberately ignores broad `GH_TOKEN`/`GITHUB_TOKEN` variables. |
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
| `METAXIS_STATE_BACKEND` | No | No | `memory` | Dynamic-state backend. Set `cloudflare-d1` only with the complete governed D1 configuration. |
| `CLOUDFLARE_ACCOUNT_ID` | For D1 | No | None | Cloudflare account coordinate for the D1 REST query API. |
| `METAXIS_D1_DATABASE_ID` | For D1 | No | None | UUID of the METAXIS dynamic-state D1 database. |
| `CLOUDFLARE_D1_API_TOKEN` | For D1 | Yes | L2 credential mesh injection | Least-privilege D1 Read/Write API token; never exposed to the brain or stored in D1. |
| `CLOUDFLARE_D1_API_TOKEN_FILE` | Preferred for D1; required by OrbStack | Yes-bearing path | None | Absolute owner-only token file mounted read-only; takes precedence over the direct-process token variable. |
| `METAXIS_D1_TIMEOUT_SECONDS` | No | No | `10` | D1 query timeout at the METAXIS adapter boundary. |
| `METAXIS_D1_API_BASE` | No | No | `https://api.cloudflare.com/client/v4` | Cloudflare API base; override only for an authorized test double. |
| `METAXIS_BRAIN_MODE` | No | No | `mock` | Selects deterministic mock or `openai-compatible`; external routing still requires the separate call flag. |
| `METAXIS_EXTERNAL_MODEL_CALLS` | For live inference | No | `0` | Final explicit live-call gate; only `1` enables adapter construction. |
| `METAXIS_BRAIN_URL` | For live inference | No | None | Registered OpenAI-compatible endpoint base URL. |
| `METAXIS_BRAIN_API_KEY` | Direct-process compatibility only | Yes | None | Inference-only key; the OrbStack installer rejects this environment form. |
| `METAXIS_BRAIN_API_KEY_FILE` | Required by OrbStack live inference | Yes-bearing path | None | Absolute owner-only inference-key file mounted read-only. Never use the endpoint-management token. |
| `METAXIS_BRAIN_PROVIDER` | For live inference | No | `registered-provider` | Provider identifier written into provenance. |
| `METAXIS_BRAIN_ROUTE_ID` | For live inference | No | `registered-api` | Registered route identifier. |
| `METAXIS_BRAIN_MODEL` | For live inference | No | Pinned Nemotron candidate | Exact model repository sent to the endpoint and recorded in provenance. |
| `METAXIS_BRAIN_REVISION` | For live inference | No | Pinned candidate SHA | Immutable model revision recorded in provenance. |
| `METAXIS_BRAIN_DEVELOPER_COUNTRY` | For route evaluation | No | `unknown` in Python; `US` in laptop installer | Provenance control input; not sufficient by itself. |
| `METAXIS_BRAIN_PLACEMENT` | For route evaluation | No | `unknown` | Registered workload placement. |
| `METAXIS_BRAIN_MAX_OUTPUT_TOKENS` | No | No | `4096` | Hard output-token ceiling enforced before the call. |
| `METAXIS_BRAIN_TIMEOUT_SECONDS` | No | No | `60` | Provider request timeout. |
| `METAXIS_BRAIN_US_PERSON_ADMIN_ONLY` | For HIGH/NOFORN | No | `0` | Evidence-backed administrative-access control flag. |
| `METAXIS_BRAIN_US_PERSON_USER_ONLY` | For HIGH/NOFORN | No | `0` | Evidence-backed workload-user control flag. |
| `METAXIS_BRAIN_US_LOCATION_ONLY` | For HIGH/NOFORN | No | `0` | Evidence-backed placement flag. |
| `METAXIS_BRAIN_EGRESS_DEFAULT_DENY` | For HIGH/NOFORN | No | `0` | Evidence-backed network-control flag. |
| `METAXIS_BRAIN_EXTERNAL_TELEMETRY_DISABLED` | For HIGH/NOFORN | No | `0` | Evidence-backed telemetry-control flag. |
| `METAXIS_BRAIN_CUSTODY_APPROVED` | For HIGH/NOFORN | No | `0` | Evidence-backed credential-custody flag. |
| `METAXIS_HIGH_NOFORN_AUTHORITY_RECORD` | For HIGH/NOFORN | No | None | Authority record required in addition to all technical controls. |

The GitHub Actions secret `YKS_OPS_SYNC_TOKEN` is repository configuration,
not a process variable consumed by Python. The workflow exposes it to the
process as `GH_TOKEN`. Its value must never appear in logs or repository files.

The D1 API token is also an L2 credential. Selecting `cloudflare-d1` without
the account ID, database UUID, and token fails startup rather than falling back
to volatile memory. When a token file is configured it must be absolute,
owner-only, nonempty, and at most 4096 bytes. The Phase 0 schema accepts
DEVELOPMENT rows only. See `docs/cloudflare-d1-storage.md`.

The NemaShells GitHub broker is disabled for live reads unless
`METAXIS_GITHUB_TOKEN_FILE` is explicitly mounted. Use a fine-grained token
selected only for `yks2.0-ops-hub` and `yks2.0-HF-METAXIS` with repository
Metadata read permission. The broker exposes a bounded repository snapshot,
never the token or raw permission object, and provides no write method. An
invalid configured secret file fails startup instead of falling back to an
environment credential.

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
