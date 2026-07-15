# SkipJack Console Design Language 1.0

Artifact ID: `MTX-ART-DL-20260715-004`  
Decision state: accepted  
Operator ruling: 2026-07-15  
Authority: YKS Ops #422  
No-orphan execution chain: #442 -> #457 -> #472 and #474 -> #475 -> #476

## Product And Brand Boundary

- **SkipJack Console Design Language (SJCDL)** is the required source design
  language for every METAXIS operator UI and for any downstream SkipJack UI
  that adopts this console family.
- **METAXIS** is the product and harness identity rendered in the reference
  console.
- **SkipJack** is the parent brand. Full application surfaces carry the exact
  endorsement `Powered by SkipJack` at the bottom-left.
- **NemaShells is not visible branding in SJCDL.** Existing implementation,
  package, launcher, and historical evidence may retain the NemaShells name
  until separately migrated, but promoted UI copy, badges, composers, and
  assistant labels use the consuming product identity. For METAXIS that means
  `METAXIS`, `MX`, and `Message METAXIS`.
- The design language supplies no runtime authority. GitHub, D1, canon,
  TESTIMONIUM, ACTA, deterministic METAXIS state, and operator rulings outrank
  every rendering.

## Reference Artifacts

| Artifact ID | Reference | Role |
| --- | --- | --- |
| `MTX-ART-UI-20260715-005` | `skipjack-console-design-language-standard-clean-v1.0.png` | Default three-column console exemplar. |
| `MTX-ART-UI-20260715-006` | `skipjack-console-design-language-complex-unpacked-v1.0.png` | Hard-maximum ten-card unpacked exemplar. |

The PNGs define operator-approved direction, not pixel-perfect implementation
proof. Components must implement this contract in code and pass conformance
checks.

## Workspace Modes

| Mode | Active information columns/cards | Use |
| --- | ---: | --- |
| Standard Clean | 3 | Default daily view: navigation/current work, dominant conversation, and combined operations. |
| Standard Unpacked | 3 | Same structure with supporting details expanded in place. |
| Expanded | 4-6 | Additional independent columns only when operation complexity or the operator requires them. |
| Complex | 7-10 | High-density situational-awareness view with compact summaries. |
| Complex Unpacked | 7-10 | High-density view with supporting details expanded in place. |

Ten is the hard maximum. Navigation, the local composer, and the slim safety
strip do not consume operational-card capacity. When capacity is full, new
information enters a queue/dock, updates an existing relevant card, or replaces
the lowest-priority unpinned card with visible notice. Pinned cards are never
silently displaced.

## Standard Geometry

The standard desktop composition uses approximately:

- 16% fixed navigation and current-work rail;
- 64% dominant conversation/work column; and
- 20% combined operations column.

The middle column is visually dominant. The right column is intentionally
about 40% narrower than the earlier inspector treatment. Current Work appears
under task/project navigation rather than as a disconnected global panel.

## Column Contract

Every operational column/card:

- scrolls independently;
- can be resized, reordered, pinned, collapsed, expanded, or focused full-width;
- retains its own task context and state;
- declares `LIVE`, `MOCK`, `STALE`, or `BLOCKED` provenance at the header;
- uses deterministic state for health, classification, authority, proof, cost,
  and route eligibility;
- keeps controls discoverable but visually quiet; and
- preserves keyboard focus order, reduced-motion behavior, and display scaling.

The composer belongs inside the conversation column it controls. It is never a
global footer. Focusing a column full-width retains that column's context and
local controls.

## Future Capability: Multi-Monitor Workspace

Every METAXIS UI shall preserve a future path to a multi-monitor workspace.
This capability is planned and deferred: it is not implemented by the 1.0
references and is not a Phase 0 conformance blocker.

The future capability shall allow the operator to move, pin, and focus columns
across connected displays while preserving one governed workspace, session,
and authority context. The ten-card hard maximum applies across the complete
workspace, not separately to each monitor. A conforming implementation shall:

- retain each column's task context, provenance, proof state, and local
  composer when moved between displays;
- make the active display and focused column unambiguous;
- restore displaced columns safely to the primary display when a monitor is
  disconnected, without losing state or silently replacing pinned work;
- support saved operator layouts without treating monitor identity or layout
  state as authorization;
- apply classification, privacy, stale-state, and blocked-state presentation
  consistently on every display; and
- retain a usable single-monitor fallback with no capability or authority
  loss.

Future acceptance requires multi-display layout persistence, disconnect and
reconnect recovery, focus and keyboard traversal across windows, scaling and
mixed-resolution checks, provenance continuity, and proof that no additional
runtime authority is created by opening another display.

## Information Density

- Summarize secondary information to one line by default.
- Use one subtle `See more` control per collapsed section/card and one `See
  less` control when unpacked.
- Hover or soft click may reveal local detail without changing authority or
  source state.
- Prefer lightweight separators and one outer boundary per column; avoid cards
  nested inside cards.
- Do not repeat a status already established by a parent/header. A single
  overall `BLOCKED` badge establishes the global posture; red is reserved for
  actual blocked or denied facts.

## Semantic Color And Motion

- Cyan: active or live.
- Green: verified, healthy, or complete.
- Amber: attention, mock, or pending.
- Red: blocked or denied.
- Neutral gray: ordinary metadata.

The seven-bar METAXIS signal is static at unequal heights while idle and under
reduced-motion preference. During processing it may use the accepted 2.6-second
staggered undulation. Motion is feedback, never proof.

## Required Conformance Declaration

Every UI implementation that adopts this design system shall declare:

```text
source_design_language: SKIPJACK-CONSOLE-DL-1.0
source_design_artifact: MTX-ART-DL-20260715-004
```

Acceptance requires snapshot coverage for Standard Clean and Complex
Unpacked, component-level state/provenance tests, keyboard and reduced-motion
checks, local-composer ownership, card-capacity enforcement, and proof that a
package or consuming product can change without forking the interaction or
authority contract.

## Non-Claims

Acceptance of SJCDL does not claim that every view is implemented, that a
desktop package is selected, that a runtime is production-ready, that D1 has a
live row, that multi-monitor operation is implemented, or that HIGH/NOFORN
processing is authorized.
