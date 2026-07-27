---
status: template
---

# <Epic Name> — Test Scenarios

> **Template.** This file defines the canonical structure for every Epic's
> test plan in this project. To create a new test file:
>
> 1. Copy this file to `E<N>-<slug>.md` (matching the spec/task Epic file)
> 2. Fill in placeholders — one row per scenario
> 3. Remove this banner when done
> 4. Commit
>
> Every scenario must map back to a requirement ID and the task(s) it
> depends on.

**Source:** [[NNN-slug]]     <!-- Backlog item that produced this file's initial write. Every scenario row also carries its own Source column below. -->

Covers <REQ-IDs>.

**Entry-point anchoring:** for every user-observable outcome in this Epic,
at least one row must start with `**Entry-point**:` — the scenario runs
from the real user-contact surface (root widget rendered via `main()`,
HTTP call with an external `Origin` header, CLI invoked via `main()`), not
from a widget/function tested in isolation. Widget/unit rows are welcome
in addition.

**Per-scenario Source:** every row has a `Source` column carrying the backlog item that produced that specific scenario in `[[NNN-slug]]` syntax. Required. This is how the file stays traceable as scenarios from many items accumulate over time.

| Scenario | Layer | Requirement | Task | Source |
|---|---|---|---|---|
| **Entry-point**: <observable behaviour via the real entry — e.g. "root widget rendered via `main()` shows the task list", "GET /api/tasks with Origin http://localhost:8080 returns 200 with `Access-Control-Allow-Origin` header"> | <Integration / E2E> | <REQ-ID> | <T<NN>> | [[NNN-slug]] |
| <Happy path — concise description of the observable behaviour> | <Unit / Slice / Integration / E2E> | <REQ-ID> | <T<NN>> | [[NNN-slug]] |
| <Validation / error case> | <Layer> | <REQ-ID, NFR-ID> | <T<NN>, T<NN>> | [[NNN-slug]] |
| <Edge case — concurrency / duplicate / missing entity> | <Layer> | <REQ-ID> | <T<NN>> | [[NNN-slug]] |
