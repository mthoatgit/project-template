---
status: template
---

# B<NN> — <Bug Title>

> **Template.** This file defines the canonical structure for every bug
> file in this project. To create a new bug file:
>
> 1. Copy this file to `E<N>/B<NN>-<slug>.md` (next free B-ID from `docs/tasks/index.md`)
> 2. Fill in header fields, Symptom, Fix approach (from the source bug item's Stage 4)
> 3. Fix commit SHA fills in when the fix lands (by orchestrator for Class A, by human for Class B)
> 4. Remove this banner and the `status: template` frontmatter
> 5. Add a row to `docs/tasks/index.md` with `Type: bug`
>
> **Note on content vs source.** This B-file is the orchestrator's
> interface — enough context for the fix to happen. The substantive
> Reproduction recipe, full Root Cause analysis, and design discussion
> live in the source bug item (in `docs/backlog/archive/`) under its
> Stage 1-4 Discussion + Outcome sub-sections. Do NOT duplicate that
> content here. This file is intentionally thin.

**Epic:** <E<N> | cross>
**Source:** [[NNN-slug]]     <!-- backlog bug item this originated from -->
**Class:** <A | B>
**Related Task(s):** <T<NN>, T<NN>>
**Pinned regression test:** <row-identifier in docs/tests/epics/E<N>-*.md marked with Source [[NNN-slug]]>
**Fix commit:** <TBD — filled when fix lands>

## Symptom

<One paragraph — plain description of the wrong behavior. This is the browsable summary; full Reproduction recipe lives in the source bug item's Stage 1 Outcome.>

## Fix approach

<One or two sentences — the minimal code change that will turn the pinned regression test GREEN. Distilled from the source bug item's Stage 4 Discussion; do NOT copy the full discussion. Enough for the orchestrator (or the human, for Class B) to plan the fix without re-doing analysis.>

<Full Reproduction, Root Cause, and design discussion in the source item's Stages 1-4 at `docs/backlog/archive/<NNN>-<slug>.md`.>
