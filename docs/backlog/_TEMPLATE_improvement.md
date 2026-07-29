---
status: template
---

# <Short title — one line>

> **Template file.** Copy to `docs/backlog/<NNN>-<slug>.md` (NNN = highest existing ID + 1, zero-padded to 3 digits; slug in kebab-case). Replace the frontmatter above with the universal item frontmatter (`type: improvement`, `status: raw`, `priority: P<N>`, `created: <today>`, `updated: <today>`, `stage: 1`, `stage_attempt: 1`) and remove this banner. See the `workflow-backlog` skill for structure and `workflow-lifecycle-featurework` for how this item's stages work.

**Lifecycle:** featurework — see `workflow-lifecycle-featurework`

## Artefacts

<Item-level index of outputs per lifecycle stage — sits BEFORE day-zero framing for at-a-glance findability. Each stage bullet starts as `pending` and is bumped in the SAME commit as its `### Outcome` write. Bumped form: nested sub-bullets, one per produced element (files with clickable link + one-line summary; within-file entities like REQ IDs each get a sub-bullet with ID + one-line summary — see `workflow-lifecycle-featurework` for the full format spec).>

- **Stage 1 (Concept):** pending
- **Stage 2 (Requirements + Epic-Birth):** pending
- **Stage 3 (Architecture):** pending
- **Stage 4 (Task-Breakdown):** pending
- **Stage 5 (Tests):** pending

## Current state

<How it works today.>

## Proposed state

<What it would become.>

## Impact

<Why the change is worth it. What future work benefits.>

<!--
Stage sections are added as the item enters each stage of the featurework lifecycle
(Stage 1 Concept → Stage 2 Requirements → Stage 3 Architecture → Stage 4 Task-Breakdown → Stage 5 Tests).
Each stage has ### Discussion (with #### YYYY-MM-DD sub-headers for dated notes) + ### Outcome (artefact link or null decision) + **Approved:** date.
See workflow-lifecycle-featurework for each stage's specifics.

Note: the `## Current state` day-zero section above captures HOW IT WORKS TODAY (frozen).
The stage Discussions capture the DESIGN of the improvement (grows as stages work through).
-->

<!--
Optional. Add when this item cross-references other items.
Remove the header entirely if it stays empty.

## Related
- [[NNN-other-item]] — <one-line reason>
-->
