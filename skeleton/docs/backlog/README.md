# Backlog

Living list of items to circle back on — bugs and changes. Universal capture-and-shape flow per the `workflow-backlog` skill.

**Scope of this backlog:** this project's product-level items — features, gaps, tweaks, and bugs that belong to THIS project. Meta-level items about the workflow itself (skills, orchestrator, conventions) belong in the upstream `project-template` backlog, not here.

**Data:** the item table lives in [`index.md`](index.md) — it is deliberately prose-free so a frontend can parse it as a pure data source. This README explains purpose and conventions.

## Structure & Conventions

- **Types.** Two: `bug`, `change`. Each type has its own template (`templates/_TEMPLATE_<type>.md`) with type-specific capture questions.
- **One file per item.** Format `<NNN>-<slug>.md` for active items, `archive/<NNN>-<slug>.md` for done/dropped/superseded. IDs are stable from assignment (global counter across all types, no renumbering). Slug in kebab-case and carries the topic keyword for grep.
- **Universal frontmatter.** New items carry `type`, `status`, `created`, `updated`, `stage`, `stage_attempt` as YAML frontmatter. `stage` starts at `1` and moves via stage-approval (or walk-back); `stage_attempt` counts attempts per stage.
- **Timestamps.** Every row in the index carries only `Created`. The item frontmatter additionally carries `updated` — bumped on every content edit (including status flip), but not mirrored into the index.
- **Stage column.** The index carries a `Stage` column in the format `N - <Name>` (e.g. `1 - Concept`, `2 - Requirements`), mirroring the frontmatter `stage` plus the stage name from the lifecycle skill.
- **Artefacts section in the item.** Every featurework item carries an `## Artefacts` section between day-zero framing and the first stage section. It indexes outputs per stage: `pending` on creation, bumped at the respective stage's outcome write with a Markdown link to the artefact (or `not applicable — <reason>`).
- **Archive-on-terminal.** Items with status `done`, `dropped`, or `superseded` live under `archive/`, and their row is removed from `index.md` — both in the same commit as the status flip. `index.md` is a current-work dashboard, not a historical ledger; history lives in the archived file itself (or `git log --follow`).
- **Cross-references.** Backlog is SoT for open discussions and the life-ledger of items. `docs/tasks/index.md` is for accepted work with a TASK/BUG file.
- **Adding.** Always collaborative. Never silent add. Adding = file op **AND** row entry in `index.md` in the **same commit**. `/backlog <type> <oneliner>` automates this.
- **Consultation.** On-demand. User asks "what's open" or points at an item.
- **Slash-Command.** `/backlog` — universal entry point. Modes:
  - `/backlog` — browse all open items grouped by type
  - `/backlog <type> <oneliner>` — new item, type given directly
  - `/backlog <oneliner>` — new item, type asked interactively
  - `/backlog <NNN-slug>` — open / extend / promote an existing item
- **Lifecycle & Stages.** Every item type is bound to a lifecycle. `workflow-lifecycle-featurework` for change (5 stages), `workflow-lifecycle-bug` for bug (4 stages).
- **Terminal exits.**
  - `done` — All applicable stages complete.
  - `dropped` — Item considered and discarded.
  - `superseded` — Item replaced by another.
  - `wont-fix` — bug-only. Decided not to fix.
  - `cant-repro` — bug-only. Stage 1 (Reproduction) ended without a reproducer.

## Sort order in `index.md`

By ID ascending. Only non-terminal items (`raw` / `in-progress`) ever appear — once status flips to a terminal value, the row is removed in the same commit as the archive move.
