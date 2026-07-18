---
status: template
---

# B<NN> — <Bug Title>

> **Template.** This file defines the canonical structure for every bug
> file in this project. To create a new bug file:
>
> 1. Copy this file to `E<N>/B<NN>-<slug>.md` (next free B-ID from `docs/tasks/index.md`)
> 2. Fill in header fields, Symptom, Reproduction (required to start work)
> 3. Root Cause and Fix fill in during handling
> 4. For Class A: the Regression Test scenario is also appended to `docs/tests/epics/E<N>-*.md`
> 5. Remove this banner and the `status: template` frontmatter
> 6. Add a row to `docs/tasks/index.md` with `Type: bug`

**Epic:** <E<N> | cross>
**Related Task(s):** <T<NN>, T<NN>>
**Class:** <A | B>
**Reported:** <YYYY-MM-DD>

## Symptom

<What the user observes — plain description of the wrong behavior. No interpretation, no root-cause guessing.>

## Reproduction

<Exact steps to reproduce. Commands, URLs, inputs. Explicit expected vs actual.>

1. <step>
2. <step>
3. **Expected:** <observable behavior that should happen>
4. **Actual:** <what happens instead>

## Root Cause

<Filled in when the bug is fixed. Two things: why did the bug exist, AND why did the tests / smoke miss it? The second question is what turns a bug into a workflow learning.>

## Regression Test

<For Class A: the scenario appended to docs/tests/epics/E<N>-*.md. Same table row format as in that file. Must be Entry-point-anchored per workflow-tests.>

<For Class B: the smoke-catalog entry that would catch this bug.>

## Fix

<Commit SHA(s), filled in when the fix lands. For Class A: single commit containing regression test + fix.>
