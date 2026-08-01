---
type: change
status: raw
created: 2026-08-01
updated: 2026-08-01
stage: 1
stage_attempt: 1
---

# Extract the orchestrator into its own repo/package instead of copying it per project

**Lifecycle:** featurework — see `workflow-lifecycle-featurework`

## Artefacts

- **Stage 1 (Concept):** pending
- **Stage 2 (Requirements + Epic-Birth):** pending
- **Stage 3 (Architecture):** pending
- **Stage 4 (Task-Breakdown):** pending
- **Stage 5 (Tests):** pending

## Core

Every `/new-project` run vendors a frozen snapshot of `skeleton/orchestrator/` into the new downstream project. Improvements and fixes made afterward never reach projects that already scaffolded — there is no update path, only drift. The idea: pull the orchestrator out into its own repository, developed through the same backlog/stage workflow project-template uses on itself. The concrete consumption mechanism (how downstream projects reference it instead of copying it — package dependency, subtree, or something else) is an open question for Stage 3 (Architecture), not decided here. A further consideration raised during capture: whatever mechanism is chosen should eventually also allow the orchestrator to be used as an importable library, not just a CLI entry point.
