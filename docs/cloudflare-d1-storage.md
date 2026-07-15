# Cloudflare D1 dynamic storage

Status: Gate 3 passed for the DEVELOPMENT prototype on 2026-07-14
Authority: YKS Ops #434 → #449 → #464; thread-runtime dependency #436 → #451 → #466

Cloudflare D1 is the durable dynamic-state backend for METAXIS thread, turn,
and append-only state-event records. The brain remains replaceable and never
receives D1 credentials or database authority.

## Boundary

- The default `memory` backend remains deterministic and process-local.
- Selecting `cloudflare-d1` is explicit and fails closed when any coordinate or
  credential is missing; it never silently falls back to memory.
- The Phase 0 D1 schema accepts `DEVELOPMENT` rows only. HIGH/NOFORN remains
  blocked before any provider call and is not written to commercial D1.
- The D1 token stays in the L2 credential mesh or an authorized CI secret
  store. OrbStack mounts it from `CLOUDFLARE_D1_API_TOKEN_FILE` as a read-only
  owner-only file. It is not committed, written into D1, exposed to the model,
  returned by operator readback, or placed in Docker environment metadata.
- D1 holds working application state and evidence references. GitHub/YKS Ops
  and canon remain requirements and product source truth; D1 does not grant
  authorization or final-action authority.

## Schema and access

The versioned migration is
`deployment/cloudflare/d1/migrations/0001_metaxis_dynamic_state.sql`.
It creates threads, turns, and append-only state events with prepared-query
access and indexes for thread reconstruction and evidence readback.

The OrbStack service uses Cloudflare's D1 REST query API with a narrowly scoped
API token. The adapter sends parameterized SQL and reconstructs the thread list
with one join, avoiding a per-thread query loop.

The live user token is limited to `Account.D1:Edit` for the named Cloudflare
account and expires on 2027-01-14. Cloudflare does not currently offer a
database-specific token resource selector, so the adapter separately pins the
exact database UUID. The token is revocable independently of the database.

## Configuration

The governed DEVELOPMENT database is `metaxis-dynamic-state`, UUID
`f5074e31-9de6-419c-aacf-4d8e3dbdf398`, in Cloudflare account
`b96eaf77142947b0455db5425da6cb68`. It was created with an `ENAM` primary
location hint. The hint is not a residency or HIGH/NOFORN control. Non-secret
coordinates are checked into `deployment/cloudflare/d1/wrangler.jsonc`.

Required when `METAXIS_STATE_BACKEND=cloudflare-d1`:

```text
CLOUDFLARE_ACCOUNT_ID=<account-id>
METAXIS_D1_DATABASE_ID=<database-uuid>
CLOUDFLARE_D1_API_TOKEN_FILE=<absolute owner-only token-file path>
```

Optional:

```text
METAXIS_D1_TIMEOUT_SECONDS=10
METAXIS_D1_API_BASE=https://api.cloudflare.com/client/v4
```

Direct-process tooling may use `CLOUDFLARE_D1_API_TOKEN` for compatibility,
but the OrbStack installer rejects that form. Do not place populated values in
`.env`. Inject the file from the approved credential boundary.

## Migration workflow

Use the checked-in DEVELOPMENT `wrangler.jsonc` and the pinned Wrangler version
selected by operations:

```text
pnpm dlx wrangler@4.110.0 d1 migrations apply metaxis-dynamic-state --local --config deployment/cloudflare/d1/wrangler.jsonc
pnpm dlx wrangler@4.110.0 d1 migrations apply metaxis-dynamic-state --remote --config deployment/cloudflare/d1/wrangler.jsonc
```

The remote migration and one restart/recovery proof passed on 2026-07-14. See
`docs/cloudflare-d1-validation-2026-07-14.md` for the redacted evidence. This is
a DEVELOPMENT prototype result, not production or HIGH/NOFORN activation.
