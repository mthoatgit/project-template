---
status: template
---

# E<N> — <Epic Name>

> **Template.** This file defines the canonical structure for every Epic
> overview file in this project. To create a new Epic:
>
> 1. Create a folder `E<N>-<slug>/` (next free Epic number, kebab-case slug)
> 2. Copy this file into it as `E<N>-<slug>/E<N>-<slug>.md`
> 3. Fill in placeholders
> 4. Remove this banner **and any optional sections that don't apply**
> 5. Commit
>
> Epic IDs are stable — never reused, never renumbered. One Epic per folder.
> Individual Functional Requirements live in per-REQ files inside the folder
> (see `_REQ-TEMPLATE.md`); this overview file holds only the index of links
> to those REQ files, plus Goal / NFRs / Dependencies.

**Status:** draft
**Branch:** `epic/<N>-<slug>`
**PR title:** `Epic <N>: <Epic Name>`
**Source:** [[NNN-slug]]     <!-- source backlog item whose Stage 2 (Requirements + Epic-Birth) created this Epic. Every Epic has an originating item under the current lifecycle model. -->

## Goal

<One-paragraph statement of what this Epic delivers and how a reviewer
can demo it after merge. Required.>

## Functional Requirements

<Index of links to per-REQ files inside this Epic's folder. Each bullet:
link to REQ file + REQ ID + one-line title + Architecture-impact tag.
Full REQ text lives in the per-REQ file (see `_REQ-TEMPLATE.md`), not
here. Add one bullet per REQ; supersession is annotated in-place with
strikethrough + "(superseded by REQ-<NNNN>)".>

- [**REQ-<NNNN>**](REQ-<NNNN>-<slug>.md) — <one-line title of the requirement> — Architecture-impact: none (no ADR)
- [**REQ-<NNNN>**](REQ-<NNNN>-<slug>.md) — <one-line title> — Architecture-impact: pending (see Stage 3)
- [**REQ-<NNNN>**](REQ-<NNNN>-<slug>.md) — <one-line title> — Architecture-impact: ADR-<NNNN> (<one-line reminder>)

## Non-Functional Requirements

> **Optional section.** Remove entirely if this Epic has no Epic-specific
> NFRs. Do not invent placeholder NFRs. NFRs stay inline in the overview
> file (not per-file). Cross-cutting NFRs go in
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

<Filled in at Stage 4 (Task-Breakdown) of the featurework lifecycle.
Links to files in `docs/tasks/E<N>/`.>

- [T<NN> — <Task title>](../../../tasks/E<N>/T<NN>-<slug>.md)

## Epic-Level Acceptance Criteria

<Filled in at Stage 4 (Task-Breakdown) of the featurework lifecycle.
User-observable behaviour that proves this Epic is done.>

- <Criterion 1>
- <Criterion 2>
