# TASK-0001 — Remove the vendored orchestrator from the scaffold

**Epic:** E1-orchestrator-extraction
**Source:** [[035-orchestrator-own-repo-package]]

## Requirements

- **REQ-0001** — the scaffold ships no orchestrator, so a newly scaffolded project contains no copy.

## Goal

`skeleton/` stops carrying the loop, which by itself stops every future `/new-project` run from vendoring it.

**Testability:** structural — a Stage 5 spec asserts the absence directly against the tree.

## Steps

- Delete `skeleton/orchestrator/` in full — fourteen modules plus `subprocess_settings.json`.
- Correct `skeleton/.gitignore`: its Python section is introduced by a comment stating that *"the orchestrator (bundled at ./orchestrator/) is stdlib-Python"*. The ignore rules themselves stay — a scaffolded project may add Python of its own — but the justification must no longer name a bundled loop.
- Confirm nothing else under `skeleton/` references the deleted path.

## Acceptance Criteria

- `skeleton/` MUST contain no orchestrator module, package, or `subprocess_settings.json`.
- No file under `skeleton/` MUST refer to a bundled orchestrator directory.
- A project created by copying `skeleton/.` MUST contain no orchestrator source, and the loop MUST run against it successfully from the shared installation.

## Dependencies

None. This deletion is independent of every other task in the Epic — `/new-project` copies `skeleton/.` wholesale, so removing the directory is the entire mechanism and needs no command change to take effect.
