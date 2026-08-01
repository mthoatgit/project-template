---
type: improvement
status: done
created: 2026-08-01
updated: 2026-08-01
stage: —
stage_attempt: —
---

# Restructure project-template into skeleton/ + own root

**Lifecycle:** featurework — see `workflow-lifecycle-featurework`

## Core

project-template had a structural dual-nature problem: the same file paths (`docs/concept.md`, `CLAUDE.md`, `docs/architecture/system-design.md`, `docs/adr/`, `docs/tasks/`, `docs/tests/`, `docs/specs/`) had to serve BOTH as pristine placeholders that `/init-project` fills downstream AND as project-template's own maintained artefacts. The marker-frontmatter mechanic (`status: template`) collapsed at exactly those single-instance files: keeping the marker meant the file could only be a placeholder; dropping the marker meant project-template's own content would leak into every downstream clone. Consequence: the 32 accumulated backlog items about the workflow itself could never be promoted through the featurework lifecycle — Stage 2 (Requirements) would have written REQ files into `docs/specs/epics/` that then leaked to every new project.

## Retro-doc — filed after the fact, not via the workflow

**Why this item is filed as `status: done` and archived immediately, not driven through the 5 stages:** the migration IS what makes stage-based development of project-template possible. Running the migration through its own Stage 2 would have hit the blocker it was solving. This is the one-time bootstrap that unlocks the workflow for all subsequent project-template improvements.

## What changed

Restructured the repo into a two-tier layout:

- **`skeleton/`** — 1:1 mirror of what a downstream project starts with. `/new-project` copies `skeleton/*` into the target directory.
- **Repo root (outside `skeleton/`)** — project-template's own artefacts (`CLAUDE.md`, `README.md`, `docs/` for its own backlog + future REQs/tasks/tests/ADRs, `orchestrator-tests/`, `pytest.ini`).

Downstream projects now inherit ONLY what lives under `skeleton/`. project-template's own real content sits at root and never leaks. `/new-project` switched from `git clone --local` + wipe-history to `cp -r skeleton/. <target>` + fresh `git init`.

## Related

- Migration commit: `2c9a1ba chore(structure): restructure into skeleton/ + project-template's own root`
- Commands + skill updates: dotfiles-claude commit `23d755b workflow: /new-project + /init-project use skeleton/ (cp-based, no clone)`
- Follow-up skeleton fix: `<commit for backlog README+index+archive>` — add missing pristine downstream files surfaced during validation.
