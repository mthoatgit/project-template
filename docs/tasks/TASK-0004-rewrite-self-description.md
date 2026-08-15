# TASK-0004 — Rewrite project-template's self-description

**Epic:** E1-orchestrator-extraction
**Source:** [[035-orchestrator-own-repo-package]]

## Requirements

- **REQ-0004** — this project's `CLAUDE.md` and `README.md` do not describe it as owning, testing, or specifying the loop.

## Related ADRs

- **ADR-0001** — the description this task writes is the readable form of that decision: files only, nothing that executes, two sibling repositories depended on rather than carried.

## Goal

Both top-level documents describe the project that exists after TASK-0003 rather than the one that existed before it.

**Testability:** structural — a Stage 5 spec asserts that no ownership claim survives and that the replacement statements are present.

## Steps

- `CLAUDE.md`: rewrite the Tech Stack table (no language, no test framework, no build tool), the Commands block (`pytest` is gone; there is no build, test, or run command), the Verification section (currently promising 164 orchestrator tests), Code Layout (`skeleton/orchestrator/` described as "the canonical orchestrator source", `orchestrator-tests/`, `pytest.ini`), the Gotchas entry about `pytest` at the repo root, and the Implementation section's `python -m orchestrator` invocation.
- Replace the Verification section rather than deleting it: state that verification is by inspection of the scaffolded result, and point at ADR-0001 for why.
- `README.md`: correct both tree diagrams — the Dual-nature layout block and the What's inside block — which name `orchestrator/`, `orchestrator-tests/`, and `pytest.ini`. Correct the prose in the Dual-nature paragraph, which cites "orchestrator tests" as an example of root-only files.
- Add to both a statement of where the loop lives and that it is installed, matching what TASK-0002 puts in the scaffold — the maintainer of this repository needs the same fact its downstream projects get.
- Point `CLAUDE.md`'s Implementation section at the console script, and note that driving this repository's own tasks with the orchestrator is not possible for E1 — see the Epic overview.

## Acceptance Criteria

- Neither document MUST claim this project owns, tests, or specifies the orchestrator.
- Neither MUST reference `skeleton/orchestrator/`, `orchestrator-tests/`, or `pytest.ini` as things that exist.
- `CLAUDE.md`'s Verification section MUST state how correctness is actually established here, and MUST NOT promise a test count.
- Both MUST name `~/dev/orchestrator` as the loop's home and state that it is installed rather than carried.
- Every path named in either document's layout description MUST exist.

## Dependencies

- **TASK-0003** — this task describes the state that deletion produces. Running it first would document paths that still exist.
