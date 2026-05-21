---
status: template
---

# <Concern Title>

> **Template.** Canonical structure for cross-cutting concerns in
> `docs/specs/cross-cutting/`. To create a new file:
>
> 1. Copy this file to `<concern-slug>.md` (e.g. `security.md`,
>    `performance.md`, `audit.md`)
> 2. Fill in placeholders
> 3. Remove this banner and the YAML frontmatter
> 4. Commit
>
> Use cross-cutting only for NFRs that span multiple Epics. Per-Epic
> NFRs stay in their Epic spec file.

## Concern

<One paragraph: what this concern is and why it does not fit in a single
Epic.>

## Requirements

<NFR-IDs with concern-specific prefixes (e.g. SEC-001, PERF-001, AUDIT-001).
IDs never change once assigned. Each requirement MUST have an indented
`Acceptance:` line describing the observable behavior that proves
compliance.>

- **<NFR-ID>** — <one-line non-functional requirement>
  **Acceptance:** <observable behavior that proves compliance>
- **<NFR-ID>** — <one-line non-functional requirement>
  **Acceptance:** <observable behavior>

## Affected Epics

<Epics that must satisfy this concern. Traceability hint for Phase 4
test coverage.>

- E<N> — <Epic name>
- E<N> — <Epic name>
