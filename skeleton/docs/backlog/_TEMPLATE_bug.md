---
status: template
---

# <Short title — one line>

> **Template file.** Copy to `docs/backlog/<NNN>-<slug>.md` (NNN = highest existing ID + 1, zero-padded to 3 digits; slug in kebab-case). Replace the frontmatter above with the universal item frontmatter (`type: bug`, `status: raw`, `priority: P<N>`, `created: <today>`, `updated: <today>`, `stage: 1`, `stage_attempt: 1`) and remove this banner. See the `workflow-backlog` skill for structure and `workflow-lifecycle-bug` for how this item's stages work.

**Lifecycle:** bug — see `workflow-lifecycle-bug`

## Symptom

<What breaks concretely — examples, error messages, IDs, log snippets. No interpretation.>

<!--
Stage sections are added as the item enters each stage of the bug lifecycle
(Stage 1 Reproduction → Stage 2 Root cause → Stage 3 Regression test → Stage 4 Fix).
Each stage has ### Discussion (with #### YYYY-MM-DD sub-headers for dated notes) + ### Outcome (artefact link or terminal) + **Approved:** date.
See workflow-lifecycle-bug for each stage's specifics, Class A vs B rules, and orchestrator interaction.

When Stage 4 (Fix) completes, the bug moves out of the backlog and becomes a BUG-<NNNN> file
directly under docs/tasks/ (flat layout) per workflow-lifecycle-bug's output layout.
-->

<!--
Optional. Add when this item cross-references other items — commonly:
- Follow-up idea/improvement when Root Cause reveals a spec gap
- Related tasks the bug undermines

Remove the header entirely if it stays empty.

## Related
- [[NNN-other-item]] — <one-line reason>
-->
