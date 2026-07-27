---
status: template
---

# E<N> — <Epic Name>

> **Template.** This file defines the canonical structure for every Epic
> spec in this project. To create a new Epic:
>
> 1. Copy this file to `E<N>-<slug>.md` (next free Epic number, kebab-case slug)
> 2. Fill in placeholders
> 3. Remove this banner **and any optional sections that don't apply**
> 4. Commit
>
> Epic IDs are stable — never reused, never renumbered. One Epic per file.

**Status:** draft
**Branch:** `epic/<N>-<slug>`
**PR title:** `Epic <N>: <Epic Name>`
**Source:** [[NNN-slug]]     <!-- source backlog item whose Stage 2 (Requirements + Epic-Birth) created this Epic. Every Epic has an originating item under the current lifecycle model. -->

## Goal

<One-paragraph statement of what this Epic delivers and how a reviewer
can demo it after merge. Required.>

## Functional Requirements

<Bullets with stable IDs (e.g. `CUST-001`, `XFER-007`). IDs never change
once assigned. Tasks and tests reference IDs, never file paths.
Each REQ carries three required indented fields:
- **`Acceptance:`** — observable behavior that proves it; product framing OK, tech stack NOT.
- **`Source:`** — the backlog item it was promoted from, `[[NNN-slug]]` syntax.
- **`Architecture-impact:`** — one of: `pending (see Stage 3)` (Stage 2 defers the decision; Stage 3 back-fills the concrete value), `none (no ADR)` (Stage 2 confident no architecture change needed), or `ADR-<NNNN>` (concrete ADR ID, typically back-filled by Stage 3 in the ADR commit). The record that Stage 3 was consciously either applied or skipped.>

- **<REQ-ID>** — <one-line requirement, Stage 2 confident no ADR>
  **Acceptance:** <observable, testable behavior — no tech stack>
  **Source:** [[NNN-slug]]
  **Architecture-impact:** none (no ADR)
- **<REQ-ID>** — <one-line requirement with plausible arch bearing>
  **Acceptance:** <observable behavior>
  **Source:** [[NNN-slug]]
  **Architecture-impact:** pending (see Stage 3)  <!-- Stage 3 back-fills to ADR-<NNNN> or downgrades to none -->
- **<REQ-ID>** — <one-line requirement, shape after Stage 3 back-fill>
  **Acceptance:** <observable behavior>
  **Source:** [[NNN-slug]]
  **Architecture-impact:** ADR-<NNNN> (<one-line reminder of what the ADR decided>)

## Non-Functional Requirements

> **Optional section.** Remove entirely if this Epic has no Epic-specific
> NFRs. Do not invent placeholder NFRs. Cross-cutting NFRs go in
> `docs/specs/cross-cutting/`, not here.

<Same `Acceptance:` rule as functional requirements — each NFR must have
an observable acceptance line.>

- **<NFR-ID>** — <one-line constraint or quality attribute>
  **Acceptance:** <observable behavior that proves compliance>
  **Source:** [[NNN-slug]]
  **Architecture-impact:** none (no ADR)  <!-- or ADR-<NNNN> if applicable -->

- **<NFR-ID>** — <one-line constraint or quality attribute>
  **Acceptance:** <observable behavior that proves compliance>
  **Source:** [[NNN-slug]]
  **Architecture-impact:** ADR-<NNNN> (<one-line reminder>)

## Dependencies

> **Optional section.** Remove entirely if this Epic has no prerequisites
> (typical for E1). Do not list trivial or implicit dependencies.

- <Earlier Epic or external prerequisite>

## Tasks

<Filled in during the Task Breakdown Phase. Links to files in
`docs/tasks/E<N>/`.>

- [T<NN> — <Task title>](../../tasks/E<N>/T<NN>-<slug>.md)

## Epic-Level Acceptance Criteria

<Filled in during the Task Breakdown Phase. User-observable behaviour
that proves this Epic is done.>

- <Criterion 1>
- <Criterion 2>
