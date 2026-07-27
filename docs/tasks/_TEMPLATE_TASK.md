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

## Requirements

<REQ-IDs this task implements or contributes to. Required.

REQ IDs are stable and never renumbered — if a REQ later gets
superseded, its ID stays; this task's reference remains an honest
record of what it originally implemented, and a new task is created
for the superseding REQ.

For direct-task shortcuts that bypassed a REQ (small trivial changes
promoted straight from a backlog item per the shortcut in
`workflow-requirements` "When to skip the spec entry"), write
`Direct task from [[NNN-slug]] (no REQ)` instead.>

- **<REQ-ID>** — <optional one-line reminder of what the REQ covers>
- **<REQ-ID>** — <optional one-line reminder>

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
