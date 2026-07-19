---
status: template
---

# <Short title — one line>

> **Template file.** Copy to `docs/backlog/<NNN>-<slug>.md` (NNN = highest existing ID + 1, zero-padded to 3 digits; slug in kebab-case). Replace the frontmatter above with the universal item frontmatter (`type: bug`, `status: raw`, `priority: P<N>`, `created: <today>`, `updated: <today>`) and remove this banner. See the `workflow-backlog` skill for the WHY behind the sections below.

## Symptom

<What breaks concretely — examples, error messages, IDs, log snippets.>

## Reproduction

<Steps, environment, or context that surfaces the defect. If not reproducible yet, say so and describe the observation instead.>

## Impact

<What future work suffers, or what silently goes wrong.>

## Notes (chronological)

### YYYY-MM-DD

<First note. What triggered the capture, what you already know, first hypothesis.>

<!--
Sections below are OPTIONAL. Add them when the item grows into needing
them. Remove the header entirely if the section stays empty.

## Related
- [[NNN-other-item]]

## Resolution
Filled when done. Link to the regression test + fix commit.
-->
