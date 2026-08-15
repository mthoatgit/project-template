# TEST-0007 — The dashboard is de-vendored and still reports

**Epic:** E1-orchestrator-extraction
**Mode:** procedural
**Source:** [[035-orchestrator-own-repo-package]]
**REQ:** REQ-0007
**Task:** TASK-0008
**Last verified:** 2026-08-15 by Claude (steps 1-3 and 5; step 4 exercised through the backend API rather than the Flutter client)

## Steps

1. Confirm no project under `~/dev` holds a vendored copy: `for d in ~/dev/*/; do test -d "$d/orchestrator" && echo "$d"; done` — expect no output.
2. Read `~/dev/orchestrator-dashboard/CLAUDE.md` end to end.
3. Determine whether the project still has a test suite of its own. If it does, run it.
4. Start the dashboard and point it at a project that the orchestrator has driven — `~/dev/orchestrator` itself qualifies, since it carries a populated `docs/tasks/index.md`.
5. Compare what the dashboard renders against that project's `docs/tasks/index.md` read directly.

## Expected observation

Step 1 matches if it produces no output at all.

Step 2 matches if the file names the console-script invocation, states the engine is installed rather than carried, names `~/dev/orchestrator` as its source, and describes what the dashboard *reads* from driven projects without implying it contains the loop. It does not match if any sentence still presents the loop as part of this project — including the comments about `orchestrator.py` and about the orchestrator's default `--test-cmd`.

Step 3 matches if the suite runs and passes, or if the project genuinely has no suite of its own. It does not match if a suite exists but fails, or if the only thing that used to run was the vendored copy's tests and their removal was not noticed.

Step 5 matches if every work item and every status the dashboard renders agrees with the index file read directly. Any discrepancy, including a row that fails to appear, does not match.

## Notes

Step 5 is the one this test exists for. The deletion itself is trivial and step 1 would catch a failure; what is genuinely at risk is the dashboard's *other* relationship with the loop — it consumes `docs/tasks/index.md` from driven projects — and an implementer removing a directory called `orchestrator/` could plausibly take the reading code with it.

Step 3 is deliberately phrased to distinguish "no suite" from "a suite that quietly stopped existing". The project carries a root `pytest.ini`, and `TASK-0008` requires establishing before deletion whether it configured the vendored copy's tests, the dashboard's own, or both. If that question was skipped, this step is where it surfaces.
