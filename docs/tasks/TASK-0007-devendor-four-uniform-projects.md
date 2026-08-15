# TASK-0007 — De-vendor the four uniform downstream projects

**Epic:** E1-orchestrator-extraction
**Source:** [[035-orchestrator-own-repo-package]]

## Requirements

- **REQ-0005** — projects that already vendored the loop are de-vendored and name the external engine instead.

## Goal

`dice-roller`, `kitchen-inventory`, `palette-picker`, and `wordfreq` stop carrying a frozen copy of the loop and start pointing at the shared installation, to the same standard TASK-0002 sets for newly scaffolded projects.

**Testability:** procedural — four separate repositories, none of which this Epic's pull request can contain.

## Steps

For each of the four repositories, as its own commit in that repository:

- Delete its `orchestrator/` directory — fourteen modules each.
- Rewrite its `CLAUDE.md` `## Implementation` section to match what TASK-0002 writes into the scaffold: the console-script invocation, the statement that the engine is installed rather than carried, and `~/dev/orchestrator` as its source. Each currently gives an invocation form and nothing else. Preserve each project's own `--test-cmd` value — `dice-roller` and `palette-picker` use `python scripts/test.py`, `kitchen-inventory` still carries the `<test-cmd>` placeholder, and `wordfreq` uses `python -m pytest` with a `--tasks docs/tasks/E1/` path that predates the flat layout.
- Check each project's `.gitignore` for a comment justifying its Python rules by the bundled loop, as `skeleton/.gitignore` does, and correct it where present.
- Confirm the loop still runs against the project from the shared installation afterwards.

The four are grouped into one task deliberately: the work is mechanically identical across them and splitting it into four near-identical files would add bookkeeping without adding clarity. `orchestrator-dashboard` is not in this group — it differs enough to be TASK-0008.

## Acceptance Criteria

- None of the four repositories MUST contain an orchestrator source directory.
- Each MUST name the console-script invocation, MUST state the engine is installed rather than carried, and MUST name where its source lives.
- Each project's own test command MUST survive unchanged.
- `wordfreq`'s stale `--tasks docs/tasks/E1/` path MUST be corrected to the flat layout in the same pass.
- The loop MUST run successfully against each of the four from the shared installation.

## Dependencies

- **TASK-0002** — sets the wording these four are brought into line with. Doing this first would mean writing the same text twice and risking divergence.
