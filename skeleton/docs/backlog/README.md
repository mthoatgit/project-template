# Backlog

Living list of items to circle back on — bugs, ideas, gaps, questions, improvements. Universal capture-and-shape flow per the `workflow-backlog` skill.

**Scope of this backlog:** this project's product-level items — features, bugs, gaps, questions, and improvements that belong to THIS project. Meta-level items about the workflow itself (skills, orchestrator, conventions) belong in the upstream `project-template` backlog, not here.

**Data:** the item table lives in [`index.md`](index.md) — it is deliberately prose-free so a frontend can parse it as a pure data source. This README explains purpose and conventions.

## Structure & Conventions

- **Types.** Five: `bug`, `idea`, `gap`, `question`, `improvement`. Each type has its own template (`_TEMPLATE_<type>.md`) with type-specific capture questions.
- **One file per item.** Format `<NNN>-<slug>.md` for active items, `archive/<NNN>-<slug>.md` for done/dropped/superseded. IDs are stable from assignment (global counter across all types, no renumbering). Slug in kebab-case and carries the topic keyword for grep.
- **Universal frontmatter.** New items carry `type`, `status`, `priority`, `created`, `updated`, `stage`, `stage_attempt` as YAML frontmatter. `stage` starts at `1` and moves via stage-approval (or walk-back); `stage_attempt` counts attempts per stage.
- **Timestamps.** Every row in the index carries `Created` and `Updated` (`YYYY-MM-DD HH:MM`). On creation: both equal. On a content edit (including status flip): bump `updated` in the frontmatter AND the `Updated` cell in the index in the same commit. Pure structural moves do NOT touch `Updated`.
- **Stage column.** The index carries a `Stage` column in the format `N - <Name>` (e.g. `1 - Concept`, `2 - Requirements`), mirroring the frontmatter `stage` plus the stage name from the lifecycle skill.
- **Artefacts section in the item.** Every featurework item carries an `## Artefacts` section between day-zero framing and the first stage section. It indexes outputs per stage: `pending` on creation, bumped at the respective stage's outcome write with a Markdown link to the artefact (or `not applicable — <reason>`).
- **Archive-on-terminal.** Items with status `done`, `dropped`, or `superseded` live under `archive/`. Move happens in the same commit as the status flip and the index update.
- **Cross-references.** Backlog is SoT for open discussions and the life-ledger of items. `docs/tasks/index.md` is for accepted work with a TASK/BUG file.
- **Adding.** Always collaborative. Never silent add. Adding = file op **AND** row entry in `index.md` in the **same commit**. `/backlog <type> <oneliner>` automates this.
- **Consultation.** On-demand. User asks "what's open" or points at an item.
- **Slash-Command.** `/backlog` — universal entry point. Modes:
  - `/backlog` — browse all open items grouped by type
  - `/backlog <type> <oneliner>` — new item, type given directly
  - `/backlog <oneliner>` — new item, type asked interactively
  - `/backlog <NNN-slug>` — open / extend / promote an existing item
- **Lifecycle & Stages.** Every item type is bound to a lifecycle. `workflow-lifecycle-featurework` for idea/gap/improvement (5 stages), `workflow-lifecycle-bug` for bug (4 stages), `workflow-lifecycle-question` for question (2 stages).
- **Terminal exits.**
  - `done` — All applicable stages complete.
  - `dropped` — Item considered and discarded.
  - `superseded` — Item replaced by another.
  - `wont-fix` — bug-only. Decided not to fix.
  - `cant-repro` — bug-only. Stage 1 (Reproduction) ended without a reproducer.

## Prioritisation

Backlog-triage priority — a "when to work on this item" signal for the item itself.

- **P1** — Do next. Something is currently slipping or broken.
- **P2** — Design known, build when convenient. Not urgent.
- **P3** — Nice to have. Low value or exploratory.

## Sort order in `index.md`

Grouped by status (open → done → dropped → superseded → wont-fix → cant-repro), within group by ID ascending.
