---
type: improvement
---

# P1 · Root Cause + Fix sections stay empty after bug fix

- **Symptom.** After a Class-A bug runs through the orchestrator, the bug file's `## Root Cause` and `## Fix` sections still read `_To be filled in during handling._`. B01 and B02 shipped this way on 2026-07-09.
- **Impact.** No written trace of *why* the bug existed or *why* the tests missed it. Same class of bug hits again → we relearn from scratch instead of reading history. Directly weakens the workflow's key value proposition.
- **Proposed shape.** New `diagnose_phase` in `orchestrator/loops.py`, between the reproducer step (`write_tests_phase`, verified RED) and the fix step (`ralph_loop`). Claude reads the failing test output + bug file and writes into `## Root Cause` BEFORE any fix. That diagnosis is pinned; Fix prompt receives it as context; Critic evaluates fix quality *against* the written diagnosis. `## Fix` section back-filled with the commit SHA after commit lands (auto).
- **Source.** 2026-07-09 session — user flagged Root Cause as "load-bearing artifact" that current setup doesn't enforce. See also `[[project_orchestrator_open_issues]]` "Root Cause not enforced".
