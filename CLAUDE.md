# project-template

## What this project is

`project-template` is the shared scaffold for every new project (`/new-project`). It is itself a maintained project: skills, orchestrator, commands, templates, workflow documentation all evolve here and propagate to downstream projects via the phased workflow.

**Dual-nature layout (added in the `skeleton/` restructure):**

- **`skeleton/`** — everything under this folder is what a fresh downstream project starts with. `/new-project` copies `skeleton/*` into the target and runs `/init-project` fill logic. Treat `skeleton/` as the read-only pristine mirror.
- **Root (`./`)** — project-template's own artifacts: this `CLAUDE.md`, `README.md`, `docs/` (project-template's real backlog + specs + tasks + tests + ADRs about ITSELF), `pytest.ini`, `orchestrator-tests/`.

When you edit downstream-facing content, edit under `skeleton/`. When you develop project-template itself (backlog item → REQ → task → test → orchestrator implementation), the work lives at root — mirroring the same folder shape that downstream projects use.

## Tech Stack

| Layer | Choice |
|---|---|
| Language / runtime | Python 3.11+ |
| Test framework | pytest (dev-only; runs against `orchestrator-tests/` with `pythonpath = skeleton orchestrator-tests`) |
| Storage | Files only — no runtime dependencies |
| Build tool | None (`python -m orchestrator` via `PYTHONPATH=skeleton`) |

## Commands

```bash
# Test project-template's own orchestrator suite
pytest

# Invoke the orchestrator on a downstream project (from inside that project's dir)
python -m orchestrator --tasks docs/tasks/ --project-dir .
```

## Verification

- `pytest` — 164 tests covering the orchestrator's Ralph Loop, DoD gates, per-task test discovery, status transitions, and helper modules.

## Dev Environment

- Python 3.11+ on PATH.
- Windows-first — but Bash-tool + PowerShell both work.
- Skills live in `~/.claude/skills/` (in the sibling `dotfiles-claude` repo). Commands live in `~/.claude/commands/`. Editing those affects EVERY project on this machine, not just project-template.

## Code Layout

- `skeleton/` — downstream mirror. `skeleton/orchestrator/` is the canonical orchestrator source; `skeleton/docs/` holds the pristine template files (`_TEMPLATE_*.md`, template-frontmatter placeholders); `skeleton/.claude/`, `skeleton/.github/` etc. are the shared config that lands in every new project.
- `docs/backlog/` — project-template's own backlog (items 001..033 about workflow / orchestrator / skills evolution).
- `docs/` — placeholder for project-template's own REQs / tasks / tests / ADRs as they get filed via the workflow (all currently empty; grows as `/backlog` items reach Stage 2+).
- `orchestrator-tests/` — pytest suite for the orchestrator. Not shipped downstream.
- `pytest.ini` — testpaths + pythonpath config for the orchestrator test suite. Not shipped downstream.

## Conventions

- Runtime code MUST stay stdlib-only. Test suite MAY use pytest features.
- Files under `skeleton/` are what downstream projects inherit. Adding a new template file there means every new project gets it going forward.
- Files at repo root (outside `skeleton/`) stay in project-template. Downstream projects do NOT inherit them.
- `pytest.ini`, `orchestrator-tests/`, and this `CLAUDE.md` are examples of root-only files (project-template's maintainer artifacts).

## Gotchas

- `pytest` at the repo root runs against `orchestrator-tests/` — NOT against any downstream project. To test a downstream project's own code, `cd` into it first.
- The `~/.claude/` directory (skills + commands + memory) is a SEPARATE git repo (`dotfiles-claude`). Committing here does not commit skill/command edits.
- Legacy commits from before the `skeleton/` restructure have `orchestrator/` at the repo root. `git log --follow orchestrator/` (or the equivalent for skeleton/orchestrator/) preserves the history across the rename.

## Implementation

For project-template's OWN self-improvement work (any of the 33 backlog items), the same phased workflow applies: `/backlog <NNN>` → Stage 1..5 → `/start-epic` → orchestrator loop. The orchestrator runs against project-template's OWN `docs/tasks/` (root, NOT `skeleton/docs/tasks/`).

```bash
python -m orchestrator --tasks docs/tasks/ --project-dir .
```

(With `pythonpath = skeleton` already set for this repo, the orchestrator module resolves correctly from root.)
