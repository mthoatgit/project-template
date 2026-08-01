---
type: improvement
status: dropped
---

# P2 · Diagnose test-infra bugs vs code bugs

- **Symptom.** When the test command errors *before* any assertion runs (Flutter not on PATH, missing dependency, wrong CWD), Ralph feeds the runner error to Claude as if the implementation were broken.
- **Impact.** Token budget wasted on fixes that will never work; the actual problem (environment, missing tool) is hidden behind a code-review-style error message.
- **Proposed shape.** Before treating a failed run as a code failure, detect "no tests ran" / "runner error" signatures (e.g. `command not found`, `FileNotFoundError`, empty test summary) and abort with a distinct exit reason `test infra broken` — clearly separated from `action needed`.
- **Source.** Earlier session, documented in `[[project_orchestrator_open_issues]]` "Ralph Loop can't tell test-infra bugs from code bugs".

## Dropped

**Dropped 2026-08-01.** Reason: backlog reset after the skeleton/ restructure (034) — not evaluated individually.
