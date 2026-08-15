# TASK-0008 — De-vendor `orchestrator-dashboard`

**Epic:** E1-orchestrator-extraction
**Source:** [[035-orchestrator-own-repo-package]]

## Requirements

- **REQ-0007** — the one project that vendored the loop is de-vendored, and it is the awkward case.

## Goal

The dashboard stops carrying its own copy of the loop without disturbing the different, legitimate relationship it has with the loop's output.

**Testability:** procedural — a separate repository, verified by inspection plus a run of the dashboard against a driven project.

## Steps

- Read the project first. Three things distinguish it, and the third is the one that matters: its vendored copy carries twelve modules where the real source carries fourteen, it holds an older `orchestrator/tests/` layout plus its own root `pytest.ini`, and it *consumes the loop's output* — it reads `docs/tasks/index.md` from the projects it reports on. That third relationship is not vendoring and MUST survive.
- Establish whether its own test suite depends on the vendored copy before deleting anything. It has a `pytest.ini` at the root and tests of its own, and the answer decides whether this is a deletion or a deletion plus a repair.
- Delete `orchestrator/` including its nested `tests/`.
- Decide what happens to the root `pytest.ini` based on the previous step — if it exists only to run the vendored copy's tests it goes, and if it also configures the dashboard's own suite it stays and is trimmed.
- Rewrite `CLAUDE.md`. Rather than only an `## Implementation` block, it describes itself in terms of `orchestrator.py` and carries comments about the orchestrator's default `--test-cmd`. Correct the ones that imply it contains the loop; leave the ones describing what it reads.
- Verify the dashboard still reports correctly on at least one driven project afterwards.

## Acceptance Criteria

- The repository MUST contain no orchestrator source directory and no orchestrator tests.
- The dashboard MUST still read the work-item indexes of the projects it reports on, and MUST still render them correctly for at least one real project.
- Its own test suite, if it has one independent of the vendored copy, MUST still run.
- Its `CLAUDE.md` MUST NOT describe it as containing the loop, and MUST still describe accurately what it reads from driven projects.

## Dependencies

- **TASK-0002** — supplies the wording for whatever reference the dashboard's `CLAUDE.md` ends up carrying.
