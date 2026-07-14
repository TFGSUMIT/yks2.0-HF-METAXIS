# Cloudflare D1 dynamic storage

Status: Phase 0 development contract  
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

## Configuration

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

Copy `wrangler.jsonc.example` to an external or ignored `wrangler.jsonc`, insert
the database UUID, and run the pinned Wrangler version selected by operations:

```text
npx wrangler d1 migrations apply metaxis-dynamic-state --local
npx wrangler d1 migrations apply metaxis-dynamic-state --remote
```

Remote creation, migration, and live writes remain external-state operations.
They require the Cloudflare account/database coordinates, a least-privilege D1
token, and an operator-approved target. Checked-in schema and passing adapter
tests do not claim a live database or production activation.
