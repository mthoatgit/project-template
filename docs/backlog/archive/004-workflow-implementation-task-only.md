---
type: improvement
status: dropped
---

# P1 · workflow-implementation skill is task-only

- **Symptom.** Skill describes tasks, `[start-epic]`, "one commit per task", `/ship-epic` — never mentions bugs, though bugs are now first-class work items in the same index and folder.
- **Impact.** Skill and reality drift. Someone loading only `workflow-implementation` won't know bugs share the same flow, folder, and commit format.
- **Proposed shape.** Update skill: bug commits alongside task commits per Epic, orchestrator processes both types via `docs/tasks/index.md`, `/ship-epic` bundles both, commit format for both is `[orchestrator] <ID> — tests pass, design approved` (feat/fix distinction not yet enforced — see item 016).
- **Source.** 2026-07-09 session review.

## Dropped

**Dropped 2026-08-01.** Reason: backlog reset after the skeleton/ restructure (034) — not evaluated individually.
