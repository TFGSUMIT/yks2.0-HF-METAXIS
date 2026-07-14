# NemaShells Tauri 2 shell

Status: Phase 0 second-shell implementation
Authority: YKS Ops #474 → #475 → #476

NemaShells Tauri is a second, presentation-only desktop shell for METAXIS. It
does not replace the Swift shell or own agent state, model credentials, policy,
Cloudflare D1 access, or action authority.

## Laptop topology

```text
PROTOS-3 login -> nemashells       -> Swift NemaShells.app
PROTOS-4 login -> nemashells-tauri -> NemaShells Tauri.app
                                      |
                                      v
                         127.0.0.1:4310 METAXIS
                                      |
                          memory or Cloudflare D1
```

Both shells consume the same loopback API. A second Docker/METAXIS service is
not required, so policy, thread, brain, and storage behavior remain consistent.
PROTOS-4 isolates the Tauri operator journey from the proven PROTOS-3 Swift
lane without creating a second product authority.

## Security posture

- Tauri 2 exposes only core window behavior and the HTTP plugin.
- HTTP permission is scoped to `http://127.0.0.1:4310/**`.
- No shell, opener, filesystem, SQL, process, or arbitrary remote HTTP plugin
  permission is enabled.
- A restrictive content security policy is checked into `tauri.conf.json`.
- The UI submits DEVELOPMENT turns only. METAXIS performs the actual route,
  classification, credential, and storage enforcement.

## Build and install

macOS requires Xcode command-line tools, Rust stable, Node, and pnpm. From the
repository root:

```text
./scripts/install-nemashells-tauri-orbstack.sh
```

Normal use:

```text
orb start PROTOS-4
orb -m PROTOS-4
yetis live
```

`yeti live`, `yetis-live`, and `yeti-live` are equivalent command aliases.
Every form dispatches to the same `nemashells-tauri` health-gated launcher; it
does not bypass METAXIS or introduce another service.

Inside the NemaShells conversation, `Yeti's live`, `Yeti live`, `Yetis live`,
and `Yeti's life` are deterministic boot triggers. They return a local YKS Ops
live brief on route `yeti-boot-local-readback` without invoking a model. The
brief reports when live GitHub, Project 18, workflow, or D1 refresh is
unavailable to the isolated runtime instead of fabricating current state.

The shell displays the active model route, HIGH/NOFORN denial, storage backend,
durability posture, and proof state. A successful mock response proves the UI
and local API path only; it does not prove live model or D1 activation.
