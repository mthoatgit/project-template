# P3 · MultiEdit deny rule cosmetic warning

- **Symptom.** Every subprocess Claude call prints: `Permission deny rule "MultiEdit(orchestrator/**)" matches no known tool — check for typos.`
- **Impact.** Cosmetic noise in orchestrator output; masks other warnings.
- **Proposed shape.** Either remove the `MultiEdit(orchestrator/**)` line from `orchestrator/subprocess_settings.json` (since `Edit(...)` + `Write(...)` cover the actual write surface), or find the correct tool name if there is one and use it.
- **Source.** Documented across multiple sessions.
