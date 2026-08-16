---
type: change
status: raw
created: 2026-08-16
updated: 2026-08-16
stage: 1
stage_attempt: 1
---

# Featurework item stays in-progress through implementation, not just through Stage 5

**Lifecycle:** featurework — see `workflow-lifecycle-featurework`

## Artefacts

- **Stage 1 (Concept):** pending
- **Stage 2 (Requirements + Epic-Birth):** pending
- **Stage 3 (Architecture):** pending
- **Stage 4 (Task-Breakdown):** pending
- **Stage 5 (Tests):** pending

## Core

Filed retrospectively from a live orchestrator-dashboard session (2026-08-16, driving `[[004-realign-with-current-workflow-baseline]]` through its 5-stage featurework lifecycle). At the end of Stage 4 (Task-Breakdown), when the assistant offered to proceed to Stage 5 (Tests) and then "archive the item" per the current skill rule, the user pushed back sharply and correctly: "Ich glaube es ist ein Fehler das Item zu archivieren direkt nach der Stage 5. Wir implementieren danach mit dem Orchestrator und eventuell könnte es passieren dass wir noch nicht fertig sind. Natürlich sind die Requirements fest aber das Item ist noch nicht erledigt. Eventuell macht es sinn die Implementierung selbst als Stage aufzunehmen. Ich will das Item erst archivieren als erledigt wenn es auch wirklich so ist."

The current `workflow-lifecycle-featurework` archives a featurework item at Stage-5-commit ("Item archives in this final commit"), before any code is written. The rationale in the current skill: Implementation is orchestrator-driven, potentially spans multiple sessions, and lives at Epic-level rather than item-level, so the item's Stage-5-close is a clean cut between spec-work and execution-work.

The user's counter: **"Item done" should mean the actual work is done**, not "the specs are ready to be executed". Archiving the item at Stage-5-close destroys the most valuable role the item's status ever had — telling a reader at a glance whether the thing is *actually* finished — precisely at the transition point where that answer changes. A reader who sees item 004 in `archive/` with status `done` naturally assumes the migration it describes has landed; they would have to open the archived file and cross-check `docs/tasks/index.md` Task statuses (and the Epic's PR-merged state) to discover that the answer is "no, only the specs are done, the implementation hasn't been touched yet."

Two candidate forms for the fix, both preserve the current spec-vs-execution separation but shift where the "done" line sits:

**Form A — Add Stage 6 (Implementation).** Extend the featurework lifecycle to six stages. Stage 6 is worked outside the item body (its work happens in TASK-files and the orchestrator), but its Outcome lands in the item's Stage 6 sub-section ("All TASK-<NNNN>..<NNNN> completed by orchestrator" or "Epic <N> merged as PR #<N>"). Item archives at Stage 6 close. Concrete pro: parallel structure with the other stages, no new semantic. Con: Stage 6 doesn't have per-stage discussion in the same shape (no design conversation to run for "implementation") — the Discussion sub-section would either be empty or become an orchestrator-run log.

**Form B — Semantic extension without new stage.** Item stays `in-progress` after Stage 5 approved. `status` flips to `done` and item archives at Epic-merge time (or when the last relevant TASK flips to `done` in `docs/tasks/index.md`). The item's `## Artefacts` section adds an "Implementation progress" bullet during this wait, tracking per-task status. No new lifecycle stage. Concrete pro: no reshuffling of stage counts, no empty-Discussion-shape awkwardness. Con: introduces a "post-Stage-5, pre-terminal" state that isn't reflected in the `stage` frontmatter field — the item is still numbered "Stage 5 approved" but is not done.

Both forms will be weighed in the Stage 1 (Concept) conversation. This item does not pre-decide between them.

**Cross-repo scope.** The change lands in `~/.claude/skills/workflow-lifecycle-featurework/` (skill definition). Additional wording touches likely needed in `~/.claude/skills/workflow-backlog/` (archive-on-terminal semantics) and `~/.claude/skills/workflow-implementation/` (how the loop signals item-completion back to the item file). Test coverage may live in a skill-doctor scenario or the workflow-eval harness.

**Reference session precedent.** For `[[004-realign-with-current-workflow-baseline]]`, the user directed the assistant to deviate from the current skill immediately: do Stage 5, but keep item 004 in `docs/backlog/` (not archive) and status `in-progress` until the Implementation Phase (orchestrator run) completes. This deviation is documented in item 004's Stage 5 Discussion. Item 004 is therefore a live pragmatic precedent for Form B — worth reading its Stage 5 Discussion when this item's Stage 1 runs.

## Related

- [[036-codify-prepare-present-confirm-style]] — filed in the same reference session (2026-08-16). Independent workflow; different concern.
- [[004-realign-with-current-workflow-baseline]] — the orchestrator-dashboard item that surfaced this design tension. Lives in orchestrator-dashboard's own `docs/backlog/`, not here. Currently pragmatically applying Form B (in-progress through implementation) with an explicit skill-deviation note in its Stage 5 Discussion.
