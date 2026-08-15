# Architecture Decision Records

ADRs capture architectural decisions and their rationale. One file per
decision, named `<NNNN>-<slug>.md` with a zero-padded sequence number.
The canonical structure lives in [`_TEMPLATE.md`](_TEMPLATE.md).

## Index

| # | Title | Status | Date |
|---|---|---|---|
| [0001](0001-tech-stack.md) | Files only, and a standing dependency on two sibling repositories | accepted | 2026-08-15 |

## Conventions

- **Sequence is global and never reused.** Superseded ADRs stay in place
  with their number — they are not deleted.
- **Status transitions:** `proposed` → `accepted` → (optionally)
  `superseded by NNNN`.
- A new ADR that supersedes an old one references the old one in its
  Status line; the old ADR's Status is updated to reflect supersession.
- ADRs are written at Stage 3 (Architecture) of a backlog item's
  featurework lifecycle — item 001's Stage 3 produces the founding
  ADR-0001 (tech stack); later items' Stage 3 produce further ADRs.
