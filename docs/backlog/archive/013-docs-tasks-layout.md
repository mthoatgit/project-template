---
type: improvement
status: dropped
---

# P2 · `docs/tasks/` folder+file layout not yet final

- **Symptom.** Current shape at `docs/tasks/` mixes concerns at the same level: `index.md` (merged work-item index), `_TEMPLATE_TASK.md` + `_TEMPLATE_BUG.md` (blueprints), and the Epic subfolders `E1/`, `E2/`, `E3/` (actual work items). Templates and the index sit as siblings to the folders they template and index.
- **Impact.** Nothing broken today. Concern is longer-term readability and mental model — a first-time reader scans four different concerns (template, template, index, Epic folders × N) in one directory listing. Also the folder name `tasks/` now holds both tasks and bugs, which is defensible but ambiguous.
- **Proposed shape.** Open — needs a discussion before proposing concrete changes. Options worth putting on the table: move templates into a subfolder (`docs/tasks/_templates/`, `docs/.templates/`), move the index up (project root, `docs/index.md`, or somewhere else), rename `docs/tasks/` to reflect that it holds both tasks and bugs, or accept the current layout and simply document the intent more clearly.
- **Source.** 2026-07-09 — user flagged the layout as not final at end of session, wants to revisit deliberately.

## Dropped

**Dropped 2026-08-01.** Reason: backlog reset after the skeleton/ restructure (034) — not evaluated individually.
