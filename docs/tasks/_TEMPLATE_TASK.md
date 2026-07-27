---
status: template
---

# T<NN> — <Task Title>

> **Template.** This file defines the canonical structure for every
> task in this project. To create a new task:
>
> 1. Copy this file to `E<N>/T<NN>-<slug>.md` (next free task number
>    within the Epic, kebab-case slug)
> 2. Fill in placeholders
> 3. Remove this banner **and any optional sections that don't apply**
> 4. Add a row to `docs/tasks/index.md` with `Type: task`
> 5. Commit
>
> Task IDs are stable — never reused, never renumbered. One task
> per file.

**Epic:** E<N> — <Epic Name>
**Source:** [[NNN-slug]]

## Requirements

<REQ-IDs this task implements or contributes to. Required — at least one REQ.

REQ IDs are stable and never renumbered — if a REQ later gets
superseded, its ID stays; this task's reference remains an honest
record of what it originally implemented, and a new task is created
for the superseding REQ.

Every task belongs to at least one REQ. There is no direct-task
shortcut without a REQ — small changes still enter the featurework
lifecycle at Stage 2 (REQ + Epic-Birth) before Stage 4 (Task-Breakdown)
produces this file.>

- **<REQ-ID>** — <optional one-line reminder of what the REQ covers>
- **<REQ-ID>** — <optional one-line reminder>

<!--
Optional section — add when the task's implementation is constrained by
one or more ADRs (technology choice, boundary rule, dependency stance).
Remove the header entirely if no ADR constrains the task.

## Related ADRs

- **ADR-<NNNN>** — <one-line reminder of what the ADR constrains>
-->

## Goal

<One sentence: what does completing this task achieve. Required.>

## Steps

<Concrete, ordered steps to complete the task. Required.>

- <Concrete step 1>
- <Concrete step 2>
- <Concrete step 3>

## Acceptance Criteria

<Observable, verifiable outcomes that prove the task is done. Required.>

- <Observable outcome 1>
- <Observable outcome 2>

## Dependencies

> **Optional section.** Remove entirely if there are no real prerequisites.
> Do not list trivial or implicit dependencies.

- <T<NN> — earlier task or external prerequisite>
