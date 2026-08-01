---
type: improvement
status: dropped
---

# P2 · Structured smoke concept

- **Symptom.** Manual smoke tests are aspirational — S25 in the dashboard's E3 test doc was labelled `Manual / smoke` but never actually ran, and that's precisely what let B01+B02 through. There's no forcing function that gates `done` behind smoke execution.
- **Impact.** Class B bugs (browser rendering, layout, real network under load, UX flow) have no systematic gate before "done" fires. Every Epic risks a repeat of the empty-page-shipped scenario.
- **Proposed shape.** User was designing this — batched, structured smoke at Epic-close (not per task, to avoid mid-flow interruption). Listing what the human must verify before merging. Design not yet complete. Once ready: Epic Acceptance Criteria could carry a `Manually smoke-verified:` bullet that `/ship-epic` refuses to skip.
- **Source.** 2026-07-09 discussion; user explicitly deferred to think it through.

## Dropped

**Dropped 2026-08-01.** Reason: backlog reset after the skeleton/ restructure (034) — not evaluated individually.
