---
status: template
---

# Architecture Decision Records

> **Template file.** Drop this block (and the frontmatter) once the first
> real ADR is added and the table below has real rows.

ADRs capture architectural decisions and their rationale. One file per
decision, named `<NNNN>-<slug>.md` with a zero-padded sequence number.
The canonical structure lives in [`_TEMPLATE.md`](_TEMPLATE.md).

## Index

| # | Title | Status | Date |
|---|---|---|---|
| 0001 | <First decision> | accepted | YYYY-MM-DD |

## Conventions

- **Sequence is global and never reused.** Superseded ADRs stay in place
  with their number — they are not deleted.
- **Status transitions:** `proposed` → `accepted` → (optionally)
  `superseded by NNNN`.
- A new ADR that supersedes an old one references the old one in its
  Status line; the old ADR's Status is updated to reflect supersession.
- ADRs are written during Phase 2 (Architecture) and whenever a
  significant architectural decision is made later.
