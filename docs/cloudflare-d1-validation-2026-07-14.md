# Cloudflare D1 DEVELOPMENT validation — 2026-07-14

Authority: YKS Ops `#434 → #449 → #464`; thread-runtime dependency
`#436 → #451 → #466`; functional-prototype task `#474 → #475 → #476`

## Outcome

Gate 3 passed for the PROTOS-4 DEVELOPMENT prototype. NemaShells wrote one
synthetic thread and turn through the provider-neutral METAXIS storage adapter,
the container restarted, and the same records were recovered from Cloudflare
D1. This does not authorize production or HIGH/NOFORN processing.

## Governed resource

- Account: `b96eaf77142947b0455db5425da6cb68`
- Database: `metaxis-dynamic-state`
- Database UUID: `f5074e31-9de6-419c-aacf-4d8e3dbdf398`
- Location hint: `ENAM` (not a residency or classification control)
- Migration: `0001_metaxis_dynamic_state.sql`
- Wrangler: `4.110.0`

The migration created `metaxis_threads`, `metaxis_turns`, and
`metaxis_state_events`, plus triggers that reject update or delete operations
against the state-event table.

## Credential boundary

The active credential is a user API token with only `Account.D1:Edit` on the
named account. It has no start-date restriction and expires at
`2027-01-14T23:59:59Z`. The value is held in an owner-only `0600` file outside
the repository, mounted read-only at `/run/secrets/metaxis_d1_token`, and is not
present in Docker environment metadata.

An initial token was rendered by browser inspection and was immediately
deleted without use. A second unusable issuance was absent from the token
inventory and its local copy was removed. Neither was mounted or used. The
final token was captured without rendering its value, verified active, and
used for this proof.

Cloudflare currently scopes the D1 permission at account level rather than a
specific database. METAXIS pins the exact database UUID independently. The
operator can turn the integration off immediately by revoking the token or by
reinstalling the runtime with `METAXIS_STATE_BACKEND=memory`.

## Restart/recovery proof

- Initial proof image: `metaxis:456ffa0155ef`
- Final installed image: `metaxis:096411074a30`
- Final local image ID:
  `sha256:f821a42bb1666e7100544b44d21b03bad3784c1af8376aea31ad5a9244e89fb1`
- Brain: `mock-local-development`
- External model calls: disabled
- Storage: `cloudflare-d1`, durable
- Thread: `a4c681ef-b293-4868-b019-62f1ce005c4f`
- Turn: `8ed9f2eb-b301-456d-8558-abdd80fe894b`
- Classification: `DEVELOPMENT`
- Route: `mock-local-development`

After `docker restart nemashells-metaxis`, `GET /api/v1/threads` returned the
same thread and one turn. The assistant response confirmed that no external
model was called and no consequential action was authorized.

The final installed image recovered the proof again. A subsequent
`yetis live` readback reported `cloudflare-d1; durable: true` and
`3 active / 4 loaded; writes denied` through `yeti-boot-local-readback`.

A `HIGH/NOFORN` turn against the recovered thread returned HTTP `403` with
`route_blocked`. D1 counts remained at `2` turns and `4` state events before
and after the denial, proving a zero durable-write delta.

## Isolation checks

- The token file is mounted read-only; the token value is not an environment
  variable.
- Docker inspection, container logs, and operator-state readback contain no
  token-shaped value.
- Stored rows were searched for the Cloudflare token prefix and contained no
  match (`2` threads, `2` turns, `4` state events; `0` matches).
- HIGH/NOFORN remains blocked before any provider call or durable state write.
- GitHub and Cloudflare general plugin writes remain denied; only the bounded
  METAXIS D1 adapter performs DEVELOPMENT state writes.

## Cost and shutdown

D1 has no continuously running compute instance for this database. Charges,
if the account exceeds its included plan allowances, are usage-based on rows
read, rows written, and storage. Revoking the token stops METAXIS access; the
database can remain without an active runtime route or can be deleted by a
separate operator decision.

## Nonclaims

This proof does not establish production readiness, U.S.-person-only
administration, approved credential custody for classified workloads, data
residency, or HIGH/NOFORN authorization.
