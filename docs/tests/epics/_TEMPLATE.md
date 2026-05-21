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

Covers <REQ-IDs>.

| Scenario | Layer | Requirement | Task |
|---|---|---|---|
| <Happy path — concise description of the observable behaviour> | <Unit / Slice / Integration / E2E> | <REQ-ID> | <T<NN>> |
| <Validation / error case> | <Layer> | <REQ-ID, NFR-ID> | <T<NN>, T<NN>> |
| <Edge case — concurrency / duplicate / missing entity> | <Layer> | <REQ-ID> | <T<NN>> |
