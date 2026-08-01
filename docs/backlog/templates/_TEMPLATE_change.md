---
status: template
---

# <Short title — one line>

> **Template file.** Copy to `docs/backlog/<NNN>-<slug>.md` (NNN = highest existing ID + 1, zero-padded to 3 digits; slug in kebab-case). Replace the frontmatter above with the universal item frontmatter (`type: change`, `status: raw`, `priority: P<N>`, `created: <today>`, `updated: <today>`, `stage: 1`, `stage_attempt: 1`) and remove this banner. See the `workflow-backlog` skill for structure and `workflow-lifecycle-featurework` for how this item's stages work.

**Lifecycle:** featurework — see `workflow-lifecycle-featurework`

## Artefacts

<Item-level index of outputs per lifecycle stage — sits BEFORE day-zero framing for at-a-glance findability. Each stage bullet starts as `pending` and is bumped in the SAME commit as its `### Outcome` write. Bumped form: nested sub-bullets, one per produced element (files with clickable link + one-line summary; within-file entities like REQ IDs each get a sub-bullet with ID + one-line summary — see `workflow-lifecycle-featurework` for the full format spec).>

- **Stage 1 (Concept):** pending
- **Stage 2 (Requirements + Epic-Birth):** pending
- **Stage 3 (Architecture):** pending
- **Stage 4 (Task-Breakdown):** pending
- **Stage 5 (Tests):** pending

## Core

<One paragraph. What the change is at its essence — a new capability, a missing capability that hurts, or a tweak/refactor to existing behavior. Write it the day the item is captured — do NOT rewrite this later. It is the seed, not the sapling. Design discussion happens later in the per-stage Discussion sub-sections.>

<!--
Stage sections are added as the item enters each stage of the featurework lifecycle
(Stage 1 Concept → Stage 2 Requirements → Stage 3 Architecture → Stage 4 Task-Breakdown → Stage 5 Tests).
Each stage has:

## Stage N — <name>

### Discussion

#### YYYY-MM-DD
<dated notes while working the stage>

### Outcome
<artefact link, OR "not applicable — <reason>" for null decision>

**Approved:** YYYY-MM-DD

See workflow-lifecycle-featurework for each stage's specifics.
-->

<!--
Optional. Add when this item cross-references other items (splits, follow-up work, dependencies).
Remove the header entirely if it stays empty.

## Related
- [[NNN-other-item]] — <one-line reason>
-->
