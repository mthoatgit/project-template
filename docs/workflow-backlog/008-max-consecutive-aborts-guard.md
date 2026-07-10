# P2 · MAX_CONSECUTIVE_ABORTS cascade guard

- **Symptom.** If K consecutive items hit `action needed`, orchestrator keeps trying the next one. The `workflow-bugs` skill documents this guard; the code doesn't implement it.
- **Impact.** When there's a systemic problem (test infra, wrong reproducer format, wrong fix strategy), the loop wastes tokens instead of surfacing that something's broken at a higher level.
- **Proposed shape.** In `orchestrator/main.py`, track consecutive `action needed` outcomes across items in a single run; when count reaches `MAX_CONSECUTIVE_ABORTS` (default 3), print a clear message ("3 items in a row aborted — systemic problem, stopping") and exit non-zero.
- **Source.** 2026-07-09 discussion; documented in `workflow-bugs` skill "Orchestrator involvement".
