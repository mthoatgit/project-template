---
status: template
---

# <Short title — one line>

> **Template file.** Copy to `docs/backlog/<NNN>-<slug>.md` (NNN = highest existing ID + 1, zero-padded to 3 digits; slug in kebab-case). Replace the frontmatter above with the universal item frontmatter (`type: question`, `status: raw`, `priority: P<N>`, `created: <today>`, `updated: <today>`, `stage: 1`, `stage_attempt: 1`) and remove this banner. See the `workflow-backlog` skill for structure and `workflow-lifecycle-question` for how this item's stages work.

**Lifecycle:** question — see `workflow-lifecycle-question`

## Question

<The actual question, one line if possible.>

## Why now

<What triggered it. What's blocked until it's answered.>

<!--
Stage sections are added as the item enters each stage of the question lifecycle
(Stage 1 Investigation → Stage 2 Answer).
Each stage has ### Discussion (with #### YYYY-MM-DD sub-headers for dated notes) + ### Outcome (findings, spike, or answer) + **Approved:** date.
See workflow-lifecycle-question for each stage's specifics — including when to run /spike vs inline research.
-->

<!--
Optional. Add when this item cross-references other items — commonly:
- Follow-up work when the answer requires a new feature/fix/investigation
- The spike ADR that produced the answer

Remove the header entirely if it stays empty.

## Related
- [[NNN-other-item]] — <one-line reason>
-->
