# METAXIS Brand Artifacts

These files record the operator-selected METAXIS identity and the accepted
SkipJack Console Design Language used by METAXIS operator interfaces.

| Artifact ID | File | Role | Posture |
| --- | --- | --- | --- |
| `MTX-ART-BRAND-20260714-001` | `metaxis-product-lockup-v0.1.svg` and `metaxis-product-lockup-v0.1.png` | Primary METAXIS product identity | current draft / manual-placeholder |
| `MTX-ART-UI-20260714-002` | `nemashells-skin-mockup-v0.1.png` | NemaShells visual projection using the selected identity | current draft / manual-placeholder |
| `MTX-ART-UI-20260714-003` | `nemashells-modular-workspace-mockup-v0.1.png` | Codex-inspired modular NemaShells operator-workspace projection | current draft / manual-placeholder |
| `MTX-ART-DL-20260715-004` | `skipjack-console-design-language-v1.0.md` | Mandatory source design language for METAXIS UIs | accepted / row-backed design receipt |
| `MTX-ART-UI-20260715-005` | `skipjack-console-design-language-standard-clean-v1.0.png` | Standard Clean reference view | accepted / row-backed design receipt |
| `MTX-ART-UI-20260715-006` | `skipjack-console-design-language-complex-unpacked-v1.0.png` | Complex Unpacked ten-card reference view | accepted / row-backed design receipt |

The 2026-07-14 NemaShells-branded UI projections are retained as superseded
history. They are not the source design language for new UI implementation.

## Identity hierarchy

- **METAXIS** is the product.
- **SkipJack** is the parent brand.
- The product lockup contains the seven-bar NSQ signal mark and `METAXIS`
  only.
- The full application skin carries the endorsement `Powered by SkipJack` at
  the bottom-left, outside the product lockup.

## Motion contract

The SVG defaults to `data-state="idle"`. When the asset is inlined into an
application, set the root SVG attribute to `data-state="processing"` while
METAXIS is working. The seven signal bars then use the site-derived 2.6-second
staggered undulation. Reduced-motion preference disables the animation and
preserves the unequal-height resting mark.

Using the SVG through an `<img>` element cannot toggle the internal state.
Surfaces that need stateful motion must inline the SVG or reproduce the motion
contract in native UI code.

## SkipJack Console Design Language

Every METAXIS UI uses `SKIPJACK-CONSOLE-DL-1.0` and cites
`MTX-ART-DL-20260715-004` as its source design artifact. The design language is
package- and product-interface-neutral: consuming products supply their own
visible identity. METAXIS surfaces use `METAXIS`, `MX`, and `Message METAXIS`;
NemaShells is not visible design-language branding.

The standard view has three information columns, a 16/64/20 desktop geometry,
a conversation-local composer, summarized secondary information, and one soft
detail disclosure per section. Expanded operation uses 4-6 cards; complex
operation uses 7-10; 10 is the hard maximum. Each operational card scrolls
independently and can be resized, reordered, pinned, collapsed, expanded, or
focused full-width while retaining context and explicit provenance.

## Historical interaction contract

- **NemaShells** is the installed operator console, interface, and application
  contract.
- **METAXIS** is the provider-neutral agentic harness behind the console.
- **SkipJack** supplies the parent brand and skin; it does not become runtime
  authority.
- The target UI substrate is a React and TypeScript component system with
  rearrangeable, collapsible, pinnable, resizable cards and saved layouts.
- The component system, design tokens, state contracts, and workflows remain
  independent from the desktop package.
- The desktop packager is an implementation detail beneath NemaShells. No
  Tauri implementation or fallback is required for acceptance. A native or
  Chromium/Electron wrapper may be evaluated only when distribution evidence
  requires one; it must not change the NemaShells interaction or authority
  contract.
- Every card must distinguish live, synthetic/mock, stale, denied, and
  unavailable data. A design mockup never proves operational state.

## Authority and provenance

- Product authority: YKS Ops issue 422.
- Implementation chain: YKS Ops issues 442 → 457 → 472 and 474 → 475 → 476.
- Product manifest: `yks2.0-ops-hub/canon/products/product-manifest.md` on the
  METAXIS product branch.
- Detailed provenance, checksums, and non-claims are recorded in
  `artifact-manifest.json`.

These are design artifacts, not production-activation, live-D1, or
HIGH/NOFORN proof.
