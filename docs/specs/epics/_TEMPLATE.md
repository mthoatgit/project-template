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

## Goal

<One-paragraph statement of what this Epic delivers and how a reviewer
can demo it after merge. Required.>

## Functional Requirements

<Bullets with stable IDs (e.g. `CUST-001`, `XFER-007`). IDs never change
once assigned. Tasks and tests reference IDs, never file paths. Required.>

- **<REQ-ID>** — <one-line requirement>
- **<REQ-ID>** — <one-line requirement>

## Non-Functional Requirements

> **Optional section.** Remove entirely if this Epic has no Epic-specific
> NFRs. Do not invent placeholder NFRs. Cross-cutting NFRs go in
> `docs/specs/cross-cutting/`, not here.

- **<NFR-ID>** — <one-line constraint or quality attribute>

## Dependencies

> **Optional section.** Remove entirely if this Epic has no prerequisites
> (typical for E1). Do not list trivial or implicit dependencies.

- <Earlier Epic or external prerequisite>

## Tasks

<Filled in during the Task Breakdown Phase. Links to files in
`docs/tasks/epics/E<N>/`.>

- [T<NN> — <Task title>](../../tasks/epics/E<N>/T<NN>-<slug>.md)

## Epic-Level Acceptance Criteria

<Filled in during the Task Breakdown Phase. User-observable behaviour
that proves this Epic is done.>

- <Criterion 1>
- <Criterion 2>
