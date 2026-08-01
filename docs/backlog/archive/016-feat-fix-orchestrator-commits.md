---
type: improvement
status: dropped
---

# P3 · Conventional-Commit distinction feat / fix for orchestrator commits

- **Symptom.** Task commits and bug commits both use the format `[orchestrator] <ID> — tests pass, design approved`. Nothing in the commit subject distinguishes a feature commit (T<NN>) from a bug commit (B<NN>) besides the ID prefix.
- **Impact.** History readers can't skim `git log` and see "these were bug fixes vs those were features" without decoding the ID prefix. Cross-tooling that consumes Conventional Commits (changelog generators, release tooling) won't classify correctly.
- **Proposed shape.** Optional: `[orchestrator] feat: T<NN> — ...` and `[orchestrator] fix: B<NN> — ...`. Requires updating `git_ops.py::get_completed_task_ids` regex to still find the ID. Trade-off: adds visual noise for a benefit that only matters if we ever consume the log programmatically.
- **Source.** 2026-07-09 discussion.

## Dropped

**Dropped 2026-08-01.** Reason: backlog reset after the skeleton/ restructure (034) — not evaluated individually.
