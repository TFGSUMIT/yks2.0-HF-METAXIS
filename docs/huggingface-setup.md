# Hugging Face Phase 0 Setup

Status: discovery-ready / authenticated connector and CLI  
Authority: YKS Ops issue 423 and requirement `YKS-REQ-MTX-025`  
Observed: 2026-07-14

## Purpose

Hugging Face is the first model and provider discovery surface for METAXIS.
This setup supports research, immutable revision capture, license and model-card
inspection, and later bounded endpoint evaluation. It does not activate an
Inference Endpoint, approve spend, select a model, or accept license terms.

## Installed Surfaces

| Surface | Version / identity | State | Boundary |
| --- | --- | --- | --- |
| Hugging Face Codex plugin | `1.0.0` / `yetisdigits` | authenticated | Governed discovery and metadata inspection; connector credentials are not exported to the worktree. |
| `hf` CLI | `1.23.0` / `yetisdigits` | OAuth authenticated; `yks-metaxis` membership and endpoint-list access observed | Interactive discovery and scoped endpoint administration are available. Automated actions require L2-injected `HF_TOKEN`. |
| `huggingface_hub` Python package | `1.23.0` | pinned optional dependency | Installed by the managed environment through `.[huggingface]`. |
| HF namespace page | `https://huggingface.co/yks-metaxis` | HTTP 200 observed | Public profile surface; no repository or production claim. |

At setup time, authenticated CLI readback reported `yetisdigits` as a member of
`yks-metaxis`. Author queries returned zero models and zero datasets for that
namespace. The public organization API route returned 404 while the profile
page returned 200; CLI membership is the accepted identity readback, but
administrative capability is not inferred.

The fine-grained token named `metaxis-inference-endpoints` was created for the
`yks-metaxis` organization with only these organization scopes:

- make calls to the organization's Inference Endpoints; and
- manage the organization's Inference Endpoints.

The value was stored as the GitHub Actions secret `HF_TOKEN`, in the macOS
Keychain service `METAXIS Hugging Face Endpoint Token`, and in the current L2
session environment. It was not written to this repository. Authenticated
readback succeeded and returned an empty endpoint list, so no endpoint or spend
was created by this setup.

## Credential Boundary

- Use the authenticated plugin for public and account-scoped discovery.
- The interactive CLI OAuth session is stored by the official CLI outside the
  repository under the user's Hugging Face cache. It is not an automation
  credential and is not claimed as L2 custody proof.
- Use one fine-grained Hugging Face user token per application or workflow.
- Hold `HF_TOKEN` in the L2 credential mesh and inject it only into the
  authorized process.
- Keep `HF_HUB_DISABLE_IMPLICIT_TOKEN=1` so public reads do not automatically
  receive the token.
- Start with read access for gated/private discovery. Create a separate scoped
  write token only when YKS Ops authorizes repository creation or upload.
- Never commit a token, persist it in `.env`, print it, or store it in the model
  provider profile.

## Current Research Readback

Authenticated plugin discovery found current NVIDIA Nemotron text-generation
repositories, including the Nano 4B, Nano 30B-A3B, Super 120B-A12B, and newer
research variants. Search results are discovery evidence only. Candidate
promotion still requires the exact repository revision, actual license,
gating, model card, runtime compatibility, hardware profile, and comparison
model record required by issue 423.

## Commands

```text
hf version
hf env
hf auth whoami --format json
hf models list --search Nemotron --author nvidia --limit 20 --format json
```

For an authorized CLI operation, inject the L2 token as `HF_TOKEN` for that
process. Do not pass the token as a command-line argument because command-line
arguments can be exposed through process inspection or logs.

## Next Gate

1. Materialize the first candidate register with immutable revisions and
   license/model-card evidence.
2. Select at least one credible non-NVIDIA comparison candidate.
3. Approve a dedicated Inference Endpoint configuration and hourly spend cap.
4. Create a separate inference-only runtime token after the endpoint exists;
   do not expose the endpoint-management token as `METAXIS_BRAIN_API_KEY`.
5. Keep Inference Endpoint deployment and spend at `activated: false` and
   `spend_cap_usd: 0` until the operator accepts the endpoint plan.
